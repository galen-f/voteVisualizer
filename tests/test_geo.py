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

def test_join_votes():
    votes = pd.DataFrame({
        'state': ['CA', 'TX', 'NY'],
        'vote': [1, 0, 1]
    })
    shapes = load_states()
    merged = join_votes(votes, shapes)
    assert not merged.empty
    assert 'vote' in merged.columns
    assert merged['vote'].isnull().sum() < len(merged)  # Some matches should exist