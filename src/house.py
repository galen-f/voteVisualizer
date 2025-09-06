import requests
import xml.etree.ElementTree as ET
import pandas as pd

def _congress_to_year(congress: int) -> int:
    return 1789 + (congress - 1) * 2

def _house_url(year: int, roll: int) -> str:
# Zero‑pad to three digits; a few historic years may exceed 999, we try both 3 and 4 just in case.
    session_paths = [f"https://clerk.house.gov/evs/{year}/roll{roll:03d}.xml",
                     f"https://clerk.house.gov/evs/{year}/roll{roll:04d}.xml"]
    for path in session_paths:
        if requests.head(path).status_code == 200:
            return path
    raise ValueError(f"No valid URL found for {year}-{roll}")

def _parse_house_members(root) -> pd.DataFrame:
    rows = []
    for rv in root.findall(".//recorded-vote"):
        leg = rv.find("legislator")
        state = (leg.get("state") if leg is not None else "").strip()
        dist  = (leg.get("district") or "").strip()
        vote  = (rv.findtext("vote") or "").strip() or "Not Voting"
        if state:
            geoid = f"{state}-{dist}".strip("-")  # e.g. CA-12 or CA if at-large
            rows.append({"geoid": geoid, "vote": vote})
    return pd.DataFrame(rows)

class HouseSource:
    def fetch(self, congress: int, roll: int) -> pd.DataFrame:
        year = _congress_to_year(congress)
        url = _house_url(year, roll)
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        return _parse_house_members(root)

def present_house_data():
    return HouseSource()