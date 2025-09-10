import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Consistent colors for categories
VOTE_PALETTE = {
    "Aye": "#2ca02c",
    "No": "#d62728",
    "Present": "#ff7f0e",
    "Not Voting": "#7f7f7f",
}


def render_map_house(gdf, title="Map", vote_col="vote", outfile=None, show=False):
    # Lazy import to avoid hard dep at import time
    from geopandas import GeoDataFrame

    if not isinstance(gdf, GeoDataFrame):
        raise TypeError("gdf must be a GeoDataFrame")
    if "geometry" not in gdf.columns:
        raise ValueError("GeoDataFrame must contain a 'geometry' column")
    if vote_col not in gdf.columns:
        raise ValueError(f"GeoDataFrame must contain '{vote_col}' for coloring")

    # Map votes -> colors. Unknowns to light gray.
    colors = gdf[vote_col].map(VOTE_PALETTE).fillna("#cccccc")

    fig, ax = plt.subplots(figsize=(10, 6))
    gdf.plot(ax=ax, color=colors, edgecolor="black", linewidth=0.2)
    ax.set_title(title)
    ax.set_axis_off()

    # Legend for categorical votes
    present_values = [
        v
        for v in ["Aye", "No", "Present", "Not Voting"]
        if v in set(gdf[vote_col].dropna().unique())
    ]
    handles = [mpatches.Patch(color=VOTE_PALETTE[v], label=v) for v in present_values]
    if handles:
        ax.legend(handles=handles, title="Vote", loc="lower left", frameon=True)

    fig.tight_layout()

    if outfile:
        fig.savefig(outfile, dpi=220, bbox_inches="tight")
        print(f"Saved {outfile} (backend {matplotlib.get_backend()})")
    if show:
        # Only works if you switch to an interactive backend
        plt.show()

    return fig, ax
