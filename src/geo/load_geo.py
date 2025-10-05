import os
import geopandas as gpd

STATE_MAP_FILE_PATH = "data/states/cb_2018_us_state_20m.shp"
DISTRICT_MAP_FILE_PATH = "data/districts/cb_2018_us_cd116_20m.shp"

state_map = STATE_MAP_FILE_PATH  # Path to the shapefile of
district_map = DISTRICT_MAP_FILE_PATH# Path to the shapefile of US congressional districts


def load_states():
    """
    Fetch the geographic data for US states from a shapefile.

    Returns
    -------
    gpd.GeoDataFrame
        A GeoDataFrame containing the geometry of US states.
    """
    if not state_map:
        raise RuntimeError("STATE_MAP_FILE_PATH is not set. Check your .env.")
    gdf = gpd.read_file(state_map)
    # print(gdf)

    # Drop hawaii and alaska - they make the map look shit and PR because it has no vote.
    gdf = gdf[~gdf["NAME"].isin(["District of Columbia", "Puerto Rico"])]

    return gdf


def load_districts():
    """
    Load the congressional district shapefile (GeoDataFrame).

    Uses the DISTRICT_MAP_FILE_PATH provided in .env.
    """
    if not district_map:
        raise RuntimeError("DISTRICT_MAP_FILE_PATH is not set. Check your .env.")
    gdf = gpd.read_file(district_map)

    # Drop non-contiguous areas if present (e.g. PR, AK, HI, GU, VI, etc)
    gdf = gdf[~gdf["STATEFP"].isin(["02", "15", "60", "66", "69", "72", "78"])]

    return gdf
