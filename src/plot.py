
import matplotlib
matplotlib.use("Agg")  # Ensure headless rendering for tests/environments without a display
import matplotlib.pyplot as plt

def render_map(gdf, title="Map"):
    """Render a simple map for a given GeoDataFrame.

    Parameters
    ----------
    gdf : GeoDataFrame
        A GeoPandas GeoDataFrame containing a 'geometry' column with polygons.
        It can be either a states layer or a congressional districts layer.
    title : str
        Title for the plot.

    Returns
    -------
    (fig, ax) : tuple
        The created Matplotlib Figure and Axes objects.
    """
    # Defensive checks to fail fast with a helpful error message
    try:
        from geopandas import GeoDataFrame  # runtime import to avoid hard dependency at module import
    except Exception as e:
        raise RuntimeError("geopandas is required to render maps") from e

    if not isinstance(gdf, GeoDataFrame):
        raise TypeError("gdf must be a GeoDataFrame")

    if "geometry" not in gdf.columns:
        raise ValueError("GeoDataFrame must contain a 'geometry' column")

    fig, ax = plt.subplots(figsize=(10, 6))
    # Plot geometries. Avoid specifying particular colors to keep defaults as instructed.
    gdf.plot(ax=ax, linewidth=0.5)
    ax.set_title(title)
    ax.set_axis_off()
    fig.tight_layout()
    return fig, ax
