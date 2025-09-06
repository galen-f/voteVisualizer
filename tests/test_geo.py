from src.geo.load_geo import load_states, load_districts

def test_load_states():
    gdf = load_states()
    assert not gdf.empty
    assert 'geometry' in gdf.columns

def test_load_districts():
    gdf = load_districts()
    assert not gdf.empty
    assert 'geometry' in gdf.columns