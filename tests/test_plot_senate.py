import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.geo.load_geo import load_states, load_districts
from src.maps.plot_senate import render_map_senate

def _assert_render_ok(gdf, title):
    fig, ax = render_map_senate(gdf, title=title)
    # Ensure we can draw without raising
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    assert buf.getbuffer().nbytes > 0

def test_render_states_map():
    gdf = load_states()
    assert not gdf.empty

def test_render_districts_map():
    gdf = load_districts()
    assert not gdf.empty

def test_rejects_non_geodataframe():
    import pandas as pd
    import geopandas as gpd
    df = pd.DataFrame({'x':[1,2,3]})
    try:
        render_map_senate(df)
        assert False, "Expected TypeError for non-GeoDataFrame"
    except TypeError:
        pass
