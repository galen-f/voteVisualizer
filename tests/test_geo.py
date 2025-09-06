from src.geo.load_geo import load_states, load_districts
from src.geo.join_geo import join_votes
import pandas as pd

def test_load_states():
    gdf = load_states()
    assert not gdf.empty
    assert 'geometry' in gdf.columns

def test_load_districts():
    gdf = load_districts()
    assert not gdf.empty
    assert 'geometry' in gdf.columns

import pandas as pd
import geopandas as gpd
import pytest
from shapely.geometry import Polygon

# import the refactored functions
from src.geo.join_geo import join_votes, join_votes_state, join_votes_district


def _toy_poly(x0=0, y0=0, w=1, h=1):
    return Polygon([(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)])


def test_join_votes_state_basic():
    # shapes with STUSPS (state postal)
    shapes = gpd.GeoDataFrame(
        {
            "STUSPS": ["CA", "TX", "NY"],
            "geometry": [_toy_poly(0, 0), _toy_poly(2, 0), _toy_poly(4, 0)],
        },
        geometry="geometry",
        crs="EPSG:4326",
    )

    # votes keyed by `state`
    votes = pd.DataFrame(
        {
            "state": ["CA", "TX"],
            "vote": ["Yea", "Nay"],
        }
    )

    out = join_votes("senate", votes, shapes)
    assert "vote" in out.columns
    # CA and TX should map; NY should be NaN
    row_ca = out.loc[out["STUSPS"] == "CA", "vote"].iloc[0]
    row_tx = out.loc[out["STUSPS"] == "TX", "vote"].iloc[0]
    row_ny = out.loc[out["STUSPS"] == "NY", "vote"].iloc[0]
    assert row_ca == "Yea"
    assert row_tx == "Nay"
    assert pd.isna(row_ny)


def test_join_votes_state_helper_equivalence():
    # Same as above, but hit the helper directly
    shapes = gpd.GeoDataFrame(
        {"STUSPS": ["CA"], "geometry": [_toy_poly()]},
        geometry="geometry",
        crs="EPSG:4326",
    )
    votes = pd.DataFrame({"state": ["CA"], "vote": ["Yea"]})
    out_direct = join_votes_state(votes, shapes)
    out_via_main = join_votes("senate", votes, shapes)
    assert out_direct.equals(out_via_main)


def test_join_votes_district_basic_geoid_match():
    # District shapes keyed by GEOID
    # Using GEOIDs like "0612" for CA-12 and "4807" for TX-07, purely synthetic here.
    shapes = gpd.GeoDataFrame(
        {
            "GEOID": ["0612", "4807", "3601"],
            "geometry": [_toy_poly(0, 0), _toy_poly(2, 0), _toy_poly(4, 0)],
        },
        geometry="geometry",
        crs="EPSG:4326",
    )

    votes = pd.DataFrame(
        {
            "geoid": ["0612", "4807"],  # must match shapes.GEOID
            "vote": ["Yea", "Nay"],
        }
    )

    out = join_votes("house", votes, shapes)
    assert "vote" in out.columns
    v_0612 = out.loc[out["GEOID"] == "0612", "vote"].iloc[0]
    v_4807 = out.loc[out["GEOID"] == "4807", "vote"].iloc[0]
    v_3601 = out.loc[out["GEOID"] == "3601", "vote"].iloc[0]
    assert v_0612 == "Yea"
    assert v_4807 == "Nay"
    assert pd.isna(v_3601)


def test_join_votes_district_aggregates_duplicates_first_wins():
    # Verify the groupby-first behavior on duplicate geoids
    shapes = gpd.GeoDataFrame(
        {"GEOID": ["0612"], "geometry": [_toy_poly()]},
        geometry="geometry",
        crs="EPSG:4326",
    )
    votes = pd.DataFrame(
        {
            "geoid": ["0612", "0612", "0612"],
            "vote": ["Yea", "Nay", "Present"],
        }
    )

    out = join_votes("house", votes, shapes)
    assert "vote" in out.columns
    # Expect the FIRST value preserved by the aggregation
    assert out.loc[out["GEOID"] == "0612", "vote"].iloc[0] == "Yea"


def test_join_votes_district_helper_equivalence():
    shapes = gpd.GeoDataFrame(
        {"GEOID": ["4807"], "geometry": [_toy_poly()]},
        geometry="geometry",
        crs="EPSG:4326",
    )
    votes = pd.DataFrame({"geoid": ["4807"], "vote": ["Nay"]})
    out_direct = join_votes_district(votes, shapes)
    out_via_main = join_votes("house", votes, shapes)
    assert out_direct.equals(out_via_main)


def test_join_votes_invalid_chamber_raises():
    shapes = gpd.GeoDataFrame(
        {"STUSPS": ["CA"], "geometry": [_toy_poly()]},
        geometry="geometry",
        crs="EPSG:4326",
    )
    votes = pd.DataFrame({"state": ["CA"], "vote": ["Yea"]})
    with pytest.raises(ValueError):
        join_votes("galactic-senate", votes, shapes)
