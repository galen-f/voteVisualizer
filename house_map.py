"""
House Vote Visualizer
Fetches U.S. House roll‑call vote data and displays results on a U.S. congressional district map
"""

import os
from dotenv import load_dotenv
import requests
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import geopandas as gpd
from typing import Optional, Tuple
from collections import defaultdict

try:
    import us  # state metadata (postal⇄FIPS)
except Exception as _e:
    us = None

# ---------------------------------------------------------------------
# Color mapping (keep style consistent with senate_map.py)
# ---------------------------------------------------------------------
COLORS = {
    "Yea": "#1A9641",         # green
    "Nay": "#D7191C",         # red
    "Present": "#FFDE26",     # yellow
    "Not Voting": "lightgray",# gray
    None: "lightgray",        # no data / vacant
}

COLOR_LABELS = {
    "Yea": "Yea",
    "Nay": "Nay",
    "Present": "Present",
    "Not Voting": "Not Voting",
}

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
load_dotenv()
DISTRICT_SHAPEFILE = os.getenv("DISTRICT_MAP_FILE_PATH")   # per user: points to local dir; do not change
STATE_SHAPEFILE = os.getenv("STATE_MAP_FILE_PATH")         # optional, for thin outline overlay


# ---------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------
def state_abbr_to_fips(state_abbr: str) -> Optional[str]:
    """Return zero‑padded 2‑digit FIPS for a state postal abbreviation."""
    if not state_abbr:
        return None
    if us is None:
        # Fallback minimal map to avoid hard dependency during static checks/tests
        fips_map = {
            "AL":"01","AK":"02","AZ":"04","AR":"05","CA":"06","CO":"08","CT":"09","DE":"10","DC":"11",
            "FL":"12","GA":"13","HI":"15","ID":"16","IL":"17","IN":"18","IA":"19","KS":"20","KY":"21",
            "LA":"22","ME":"23","MD":"24","MA":"25","MI":"26","MN":"27","MS":"28","MO":"29","MT":"30",
            "NE":"31","NV":"32","NH":"33","NJ":"34","NM":"35","NY":"36","NC":"37","ND":"38","OH":"39",
            "OK":"40","OR":"41","PA":"42","RI":"44","SC":"45","SD":"46","TN":"47","TX":"48","UT":"49",
            "VT":"50","VA":"51","WA":"53","WV":"54","WI":"55","WY":"56","PR":"72","GU":"66","VI":"78","AS":"60","MP":"69"
        }
        return fips_map.get(state_abbr.upper())
    st = us.states.lookup(state_abbr)
    return getattr(st, "fips", None)


def normalize_district_to_3digits(district: str | int | None) -> str:
    """
    Convert a House 'district' value from Clerk XML into 3‑digit code used in shapefiles' GEOID.
    At‑Large seats and zeros are '000'.
    """
    if district is None:
        return "000"
    # Clerk XML often uses "At-Large" or "0" for at‑large.
    s = str(district).strip()
    if s.lower() in {"al", "at-large", "at large", "0", "00"}:
        return "000"
    # Some XML uses integers; ensure padding
    try:
        return f"{int(s):03d}"
    except ValueError:
        # Last resort: strip non‑digits and pad
        digits = "".join(ch for ch in s if ch.isdigit())
        if digits == "":
            return "000"
        return f"{int(digits):03d}"


def compute_geoid(state_abbr: str, district: str | int | None) -> Optional[str]:
    """
    Build the district GEOID used by the Census/Cartographic boundary shapefiles: SS + DDD.
    Example: CA‑12 -> '06' + '012' = '06012'. WY at‑large -> '56' + '000' = '56000'.
    """
    fips = state_abbr_to_fips(state_abbr)
    if not fips:
        return None
    cd3 = normalize_district_to_3digits(district)
    return f"{fips}{cd3}"


# ---------------------------------------------------------------------
# Data Acquisition
# ---------------------------------------------------------------------
def fetch_vote_data(year: int, roll_call: int) -> pd.DataFrame:
    """
    Fetch a U.S. House roll‑call vote from the Clerk XML feed and return a DataFrame.

    Parameters
    ----------
    year : int
        Calendar year for the vote (e.g., 2025).
    roll_call : int
        Roll‑call number (commonly 3 digits, left‑padded in the XML URL).

    Returns
    -------
    pd.DataFrame
        Columns:  state | district | vote | geoid
        One row per voting Member (includes 'Not Voting').
    """
    # Pattern documented by the Clerk's EVS archive, e.g.:
    # https://clerk.house.gov/evs/2025/roll207.xml
    # Zero‑pad to three digits; a few historic years may exceed 999, we try both 3 and 4 just in case.
    session_paths = [f"https://clerk.house.gov/evs/{year}/roll{roll_call:03d}.xml",
                     f"https://clerk.house.gov/evs/{year}/roll{roll_call:04d}.xml"]

    last_exc: Optional[Exception] = None
    text: Optional[str] = None
    for url in session_paths:
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            text = resp.text
            break
        except Exception as e:
            last_exc = e
            text = None

    if text is None:
        raise RuntimeError(f"Could not fetch House vote XML for year={year} roll={roll_call}: {last_exc}")

    root = ET.fromstring(text)
    # Typical structure: <rollcall-vote> -> <vote-data> -> <recorded-vote>
    rows = []
    for rv in root.findall(".//recorded-vote"):
        legislator = rv.find("legislator")
        vote_el = rv.find("vote")
        if legislator is None or vote_el is None:
            continue
        state = legislator.attrib.get("state")
        district = legislator.attrib.get("district")
        vote_txt = (vote_el.text or "").strip() or None  # "Yea" | "Nay" | "Present" | "Not Voting"
        geoid = compute_geoid(state, district)
        rows.append({"state": state, "district": district, "vote": vote_txt, "geoid": geoid})

    df = pd.DataFrame(rows)
    # Normalize vote strings to our keys
    df["vote"] = df["vote"].map(lambda v: v if v in COLORS else ("Not Voting" if pd.isna(v) else v))
    return df


def _detect_cd_col(gdf: gpd.GeoDataFrame) -> Optional[str]:
    """
    Try to infer the 'CDxxx' column if the project prefers it.
    Not strictly needed since we merge on GEOID, but handy for debugging/labels.
    """
    for col in gdf.columns:
        if col.upper().startswith("CD") and any(ch.isdigit() for ch in col):
            return col
    return None


def fetch_geographic_data() -> gpd.GeoDataFrame:
    """
    Load the congressional district shapefile (GeoDataFrame).

    Uses the DISTRICT_MAP_FILE_PATH provided in .env.
    """
    if not DISTRICT_SHAPEFILE:
        raise RuntimeError("DISTRICT_MAP_FILE_PATH is not set. Check your .env.")
    gdf = gpd.read_file(DISTRICT_SHAPEFILE)

    # Drop non-contiguous areas if present (e.g. PR, AK, HI, GU, VI, etc)
    gdf = gdf[~gdf['STATEFP'].isin(['02', '15', '60', '66', '69', '72', '78'])]

    return gdf


def merge_dataframes(df: pd.DataFrame, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Join vote data to shapes on GEOID.
    """
    # Deduplicate in case of multiple records per district (shouldn't happen, but be defensive)
    df_agg = df.groupby("geoid", as_index=False)["vote"].first()
    merged = gdf.merge(
        df_agg, 
        how="left", 
        left_on="GEOID", 
        right_on="geoid")
    return merged


# ---------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------
def plot_votes(gdf: gpd.GeoDataFrame, title: Optional[str] = None):
    """
    Plot House votes across districts.
    """
    # Map each row to a color
    def row_color(v):
        return COLORS.get(v, COLORS[None])

    # Create a color Series aligned to gdf
    colors = gdf["vote"].map(row_color).fillna('lightgray')

    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    gdf.plot(ax=ax, color=colors, linewidth=0.15, edgecolor="white")

    # # Optional: thin state outlines for context
    # try:
    #     if STATE_SHAPEFILE and os.path.exists(STATE_SHAPEFILE):
    #         states = gpd.read_file(STATE_SHAPEFILE)
    #         states.boundary.plot(ax=ax, linewidth=0.5, edgecolor="black", alpha=0.6)
    # except Exception as e:
    #     # Do not hard‑fail if state overlay breaks; the district map is still informative
    #     print(f"(warning) Could not overlay state boundaries: {e}")

    ax.set_axis_off()
    if not title:
        title = "U.S. House Roll‑Call Vote by Congressional District"
    ax.set_title(title, fontsize=14, pad=10)

    # Legend
    handles = [patches.Patch(color=COLORS[k], label=COLOR_LABELS[k]) for k in ["Yea","Nay","Present","Not Voting"]]
    leg = ax.legend(handles=handles, loc="lower left", frameon=True, title="Vote")
    leg.get_frame().set_alpha(0.8)

    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------
def main():
    print("House Vote Visualizer")
    print("---------------------")
    print("This will download a House roll‑call vote and color congressional districts.")
    print("You will be prompted for the calendar year and the roll‑call number.")
    print()

    year = input("Enter the calendar year of the vote (e.g., 2025): ").strip()
    roll_call = input("Enter the roll‑call number (e.g., 207): ").strip()

    try:
        year_i = int(year)
        roll_i = int(roll_call)
    except ValueError:
        raise SystemExit("Both year and roll‑call must be integers.")

    print(f"Fetching House vote data for year {year_i}, roll {roll_i}...")
    df = fetch_vote_data(year_i, roll_i)

    print("Loading congressional district shapes...")
    gdf = fetch_geographic_data()

    print("Merging vote data with shapes...")
    merged_gdf = merge_dataframes(df, gdf)

    title = f"U.S. House Roll‑Call Vote • {year_i} • Roll {roll_i}"
    print("Rendering map...")
    plot_votes(merged_gdf, title=title)


if __name__ == "__main__":
    main()
else:
    print("This script is intended to be run as a standalone program.")
    print("Please run it directly to visualize U.S. House votes.")
