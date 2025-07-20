"""
Senate Vote Visualizer
Fetches US Senate vote data and displays results on a US map
"""

import requests
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import geopandas as gpd
from collections import defaultdict

# Color mapping
COLORS = {
    4: '#1CE67D',  # Both Yea
    0: '#F5311B',  # Both Nay
    1: '#FF9421',  # 1 Nay, 1 no vote
    2: '#FFDE26',  # 1 yay, 1 nay
    3: '#90FF21',  # 1 yay, 1 no vote
    -1: 'lightgray', # Both no votes
}

COLOR_LABELS = {
    -1: "Both absent",
    0: "Both Nay",
    1: "Split (Nay/Absent)",
    2: "Split (Yea/Nay)",
    3: "Split (Yea/Absent)",
    4: "Both Yea"
}

shape_file = "/Users/Asus/Repositories/VoteMapMaker/StateShapeFiles/cb_2018_us_state_20m.shp"  # Path to the shapefile of US states

def __init__(self):
    self.vote_data = {}
    self.vote_info = {}

# ----------------------------------------------
# 1.  Build a mapping dictionary (or use 'us' lib)
# ----------------------------------------------
STATE_ABBREVIATION_TO_NAME = {
    'AL': 'Alabama',       'AK': 'Alaska',
    'AZ': 'Arizona',       'AR': 'Arkansas',
    'CA': 'California',    'CO': 'Colorado',
    'CT': 'Connecticut',   'DE': 'Delaware',
    'FL': 'Florida',       'GA': 'Georgia',
    'HI': 'Hawaii',        'ID': 'Idaho',
    'IL': 'Illinois',      'IN': 'Indiana',
    'IA': 'Iowa',          'KS': 'Kansas',
    'KY': 'Kentucky',      'LA': 'Louisiana',
    'ME': 'Maine',         'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan',
    'MN': 'Minnesota',     'MS': 'Mississippi',
    'MO': 'Missouri',      'MT': 'Montana',
    'NE': 'Nebraska',      'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico',    'NY': 'New York',
    'NC': 'North Carolina','ND': 'North Dakota',
    'OH': 'Ohio',          'OK': 'Oklahoma',
    'OR': 'Oregon',        'PA': 'Pennsylvania',
    'RI': 'Rhode Island',  'SC': 'South Carolina',
    'SD': 'South Dakota',  'TN': 'Tennessee',
    'TX': 'Texas',         'UT': 'Utah',
    'VT': 'Vermont',       'VA': 'Virginia',
    'WA': 'Washington',    'WV': 'West Virginia',
    'WI': 'Wisconsin',     'WY': 'Wyoming',
}
    

def fetch_vote_data(congress: int, session: int, roll_call: int) -> pd.DataFrame:
        """
        Fetch a roll‑call vote and return it as a DataFrame.

        Returns
        -------
        pd.DataFrame
            Columns:  state | vote1 | vote2
            Each row holds the two recorded votes for that state
            (None if a senator did not vote or seat is vacant).
        """
        url = (f"https://www.senate.gov/legislative/LIS/roll_call_votes/"
               f"vote{congress}{session}/vote_{congress:03d}_{session}_{roll_call:05d}.xml")

        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            root = ET.fromstring(r.content)

            # --- collect votes ------------------------------------------------
            by_state = defaultdict(list)
            for member in root.findall("./members/member"):
                state = member.findtext("state")
                vote  = member.findtext("vote_cast", default="Not Voting")
                by_state[state].append(vote)

            # --- normalize to exactly two votes per state --------------------
            rows = []
            for state, votes in by_state.items():
                # pad or truncate to length 2
                pair = (votes + [None, None])[:2]
                rows.append({"state": state, "vote1": pair[0], "vote2": pair[1]})

            # build tidy DataFrame
            df = (pd.DataFrame(rows)
                    .sort_values("state")
                    .reset_index(drop=True))
            
            # --- Classify the state vote  ---
            '''
            -1 = both votes are absent / not voting
            0 = both votes are nay
            1 = 1 not voting, 1 nay
            2 = 1 yay, 1 nay
            3 = 1 not voting, 1 yay
            4 = both votes are yay
            '''
            def no_vote(v): # Treat both absent and abstaining as equivalent
                return v in [None, 'Not Voting', 'Absent']
            
            def classify_vote(vote1, vote2):

                if no_vote(vote1) and no_vote(vote2):                                               return -1
                elif vote1 == 'Nay' and vote2 == 'Nay':                                             return 0
                elif (no_vote(vote1) and vote2 == 'Nay') or (vote1 == 'Nay' and no_vote(vote2)):    return 1
                elif (vote1 == 'Yea' and vote2 == 'Nay') or (vote1 == 'Nay' and vote2 == 'Yea'):    return 2
                elif (no_vote(vote1) and vote2 == 'Yea') or (vote1 == 'Yea' and no_vote(vote2)):    return 3
                elif vote1 == 'Yea' and vote2 == 'Yea':                                             return 4
                else:                                                                               return None

            df['orientation'] = df.apply(lambda r: classify_vote(r['vote1'], r['vote2']), axis=1)
            return df

        except (requests.RequestException, ET.ParseError) as e:
            raise RuntimeError(f"Unable to fetch or parse vote data: {e}") from e


def fetch_geographic_data() -> gpd.GeoDataFrame:
    """
    Fetch the geographic data for US states from a shapefile.
    
    Returns
    -------
    gpd.GeoDataFrame
        A GeoDataFrame containing the geometry of US states.
    """
    try:
        gdf = gpd.read_file(shape_file)
        # print(gdf)

        # Drop non-voting juristictions (DC, PR, etc.)
        gdf = gdf[gdf['STUSPS'].isin(STATE_ABBREVIATION_TO_NAME.keys())]

        # Drop hawaii and alaska - they make the map look shit.
        gdf = gdf[~gdf['NAME'].isin(['Alaska', 'Hawaii'])]

        return gdf
    except Exception as e:
        raise RuntimeError(f"Unable to fetch geographic data: {e}") from e


def merge_dataframes(df: pd.DataFrame, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Merge the vote DataFrame with the geographic GeoDataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing vote data.
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing geographic data.
    
    Returns
    -------
    gpd.GeoDataFrame
        Merged GeoDataFrame with vote data.
    """
    gdf = pd.merge(
        left=gdf,
        right=df,
        left_on='STUSPS',
        right_on='state',
        how='left')
    return gdf


def plot_votes(gdf: gpd.GeoDataFrame):
    """
    Plot the votes on a map of the US.
    
    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing geographic and vote data.
    """
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    
    # Create a color map based on the votes
    colors = gdf['orientation'].map(COLORS).fillna('lightgray')
    
    # Plot the states with their respective colors
    gdf.boundary.plot(ax=ax, linewidth=0.2, edgecolor='black')
    gdf.plot(ax=ax, color=colors, edgecolor='black')

    # Add the legend for the vote orientations from COLOR_LABELS
    legend_patches = [
        patches.Patch(facecolor=COLORS[orientation], label=label)
        for orientation, label in COLOR_LABELS.items()
    ]
    ax.legend(handles=legend_patches, loc='lower left', title='Vote Orientation')

    plt.title("US Senate Votes")
    plt.axis('off')
    plt.show()

    # Legend
    plt.legend_elements = [
        (patches.Patch(color=color, label=label) for label, color in COLORS.items())
    ]


def main():
    print('=' * 40)
    print("US Senate Vote Visualizer")
    print('=' * 40)

    congress = input("Enter a congress (e.g., 119): ")
    session = input("Enter a session (1 or 2): ")
    roll_call = input("Enter a roll call number (e.g., 416): ")

    print(f"Fetching vote data for Congress {congress}, Session {session}, Roll Call {roll_call}...")
    df = fetch_vote_data(int(congress), int(session), int(roll_call))

    print("Fetching geographic data...")
    gdf = fetch_geographic_data()

    print("Merging dataframes...")
    merged_df = merge_dataframes(df, gdf)

    print("Preparing Visualization...")
    plot_votes(merged_df)


if __name__ == "__main__":
    main()
else:
    print("This script is intended to be run as a standalone program.")
    print("Please run it directly to visualize US Senate votes.")