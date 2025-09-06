import pandas as pd
import geopandas as gpd

def join_votes(chamber, votes, shapes):
    # Detect if house or senate via the chamber argument
    if chamber == "senate":
        return join_votes_state(votes, shapes)
    elif chamber == "house":
        return join_votes_district(votes, shapes)
    else:
        raise ValueError("Invalid chamber")

def join_votes_state(votes, shapes):
    joined = pd.merge(
        left=shapes,
        right=votes,
        left_on='STUSPS',
        right_on='state',
        how='left')
    return joined

def join_votes_district(votes, shapes):
    df_agg = votes.groupby("geoid", as_index=False)["vote"].first()
    merged = shapes.merge(
        df_agg,
        how="left",
        left_on="GEOID",
        right_on="geoid")
    return merged