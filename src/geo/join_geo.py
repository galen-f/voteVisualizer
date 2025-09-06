import pandas as pd
import geopandas as gpd

def join_votes(votes, shapes):
    shapes = pd.merge(
        left=shapes,
        right=votes,
        left_on='STUSPS',
        right_on='state',
        how='left')
    return shapes