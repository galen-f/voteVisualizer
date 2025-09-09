import requests
import xml.etree.ElementTree as ET
import pandas as pd

def _senate_url(congress: int, session: int, roll: int) -> str:
    return (
        f"https://www.senate.gov/legislative/LIS/roll_call_votes/"
        f"vote{congress}{session}/vote_{congress:03d}_{session}_{roll:05d}.xml"
    )

def _parse_senate_members(root) -> pd.DataFrame:
    rows = []
    for m in root.findall("./members/member"):
        state = (m.findtext("state") or "").strip()
        vote = (m.findtext("vote_cast") or "").strip() or "Not Voting"
        if state:
            rows.append({"geoid": state, "vote": vote})
    return pd.DataFrame(rows)

class SenateSource:
    def fetch(self, congress: int, session: int, roll: int) -> pd.DataFrame:
        print("Fetching Senate Data...")
        url = _senate_url(congress, session, roll)
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        return _parse_senate_members(root)

def present_senate_data():
    return SenateSource()
