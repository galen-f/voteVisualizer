import pandas as pd


def join_votes(chamber, votes, shapes):
    # Detect if house or senate via the chamber argument
    if chamber == "senate":
        print("Joining states and senate Data...")
        return join_votes_state(votes, shapes)
    elif chamber == "house":
        print("Joining districts and house Data...")
        return join_votes_district(votes, shapes)
    else:
        raise ValueError("Invalid chamber")


# Helper function to join votes with shapes for senate (states)
def join_votes_state(votes, shapes):
    joined = pd.merge(
        left=shapes, right=votes, left_on="STUSPS", right_on="geoid", how="left"
    )
    return joined


# Helper function to join votes with shapes for house (districts)
def join_votes_district(votes, shapes):
    df_agg = votes.groupby("geoid", as_index=False)["vote"].first()
    merged = shapes.merge(df_agg, how="left", left_on="GEOID", right_on="geoid")
    return merged
