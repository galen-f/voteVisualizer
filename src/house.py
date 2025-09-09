import requests
import xml.etree.ElementTree as ET
import pandas as pd

STATEFP = {
    "AL":"01","AK":"02","AZ":"04","AR":"05","CA":"06","CO":"08","CT":"09","DE":"10","DC":"11",
    "FL":"12","GA":"13","HI":"15","ID":"16","IL":"17","IN":"18","IA":"19","KS":"20","KY":"21",
    "LA":"22","ME":"23","MD":"24","MA":"25","MI":"26","MN":"27","MS":"28","MO":"29","MT":"30",
    "NE":"31","NV":"32","NH":"33","NJ":"34","NM":"35","NY":"36","NC":"37","ND":"38","OH":"39",
    "OK":"40","OR":"41","PA":"42","RI":"44","SC":"45","SD":"46","TN":"47","TX":"48","UT":"49",
    "VT":"50","VA":"51","WA":"53","WV":"54","WI":"55","WY":"56","PR":"72","VI":"78","GU":"66",
    "MP":"69","AS":"60"
}

MEMBER_URL = "https://clerk.house.gov/xml/lists/memberdata.xml"

def _congress_to_year(congress: int) -> int:
    return 1789 + (congress - 1) * 2

def _house_url(year: int, roll: int) -> str:
    # if you already know the exact url, you can skip the HEADs and return it directly
    for path in (f"https://clerk.house.gov/evs/{year}/roll{roll:03d}.xml",
                 f"https://clerk.house.gov/evs/{year}/roll{roll:04d}.xml"):
        try:
            if requests.head(path, timeout=10).status_code == 200:
                return path
        except requests.RequestException:
            pass
    raise ValueError(f"No valid URL found for {year}-{roll}")

def _parse_house_roll(root) -> pd.DataFrame:
    rows = []
    for rv in root.findall(".//recorded-vote"):
        leg = rv.find("legislator")
        if leg is None:
            continue
        bioguide = (leg.get("name-id") or "").strip()
        state = (leg.get("state") or "").strip()
        vote = (rv.findtext("vote") or "").strip()
        rows.append({"bioguide": bioguide, "state": state, "vote": vote})
    return pd.DataFrame(rows)

def _load_member_map_from_web() -> dict:
    r = requests.get(MEMBER_URL, timeout=20)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    mapping = {}
    for m in root.findall(".//member"):
        bid = (m.findtext(".//bioguideID") or "").strip()
        sd = (m.findtext(".//statedistrict") or "").strip()  # e.g., 'NY10', 'UT01', 'AK00'
        if bid and len(sd) >= 3:
            mapping[bid] = sd
    return mapping

def _build_geoid_df(votes_df: pd.DataFrame, bioguide_to_sd: dict) -> pd.DataFrame:
    out = []
    for _, r in votes_df.iterrows():
        sd = bioguide_to_sd.get(r["bioguide"], "")
        if not sd:
            continue
        state_abbr, dist = sd[:2], sd[2:].zfill(2) if sd[2:] else ""
        statefp = STATEFP.get(state_abbr, "")
        if statefp and dist:
            geoid = f"{statefp}{dist}"
            out.append({"geoid": geoid, "vote": r["vote"]})
    return pd.DataFrame(out)

class HouseSource:
    def fetch(self, congress: int, roll: int) -> pd.DataFrame:
        year = _congress_to_year(congress)
        url = _house_url(year, roll)
        r = requests.get(url, timeout=20)
        r.raise_for_status()

        votes_df = _parse_house_roll(ET.fromstring(r.content))
        member_map = _load_member_map_from_web()  # <-- the real roster, not r.content
        result = _build_geoid_df(votes_df, member_map)

        # quick sanity logs
        print(f"votes: {len(votes_df)}  mapped: {len(result)}  unmapped: {len(votes_df)-len(result)}")
        return result

def present_house_data():
    return HouseSource()
