# src/maps/plot_senate.py
import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import geopandas as gpd

# Map all possible labels to a consistent set
VOTE_NORMALIZE = {
    "Aye": "Yea", "Yes": "Yea", "Yea": "Yea",
    "No": "Nay", "Nay": "Nay",
    "Present": "Present",
    "Not Voting": "Not Voting", "NotVoting": "Not Voting", "Absent": "Not Voting"
}
VOTE_PALETTE = {
    "Yea": "#2ca02c",
    "Nay": "#d62728",
    "Present": "#ff7f0e",
    "Not Voting": "#7f7f7f",
}

def _normalize_vote(v):
    if v is None:
        return "Not Voting"
    return VOTE_NORMALIZE.get(str(v).strip(), str(v).strip())

def _to_albers(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    # Albers Equal Area (USA)
    if gdf.crs is None:
        # assume WGS84 if missing
        gdf = gdf.set_crs("EPSG:4326", allow_override=True)
    return gdf.to_crs("EPSG:5070")

def _two_votes_per_state(df: pd.DataFrame, state_col: str, vote_col: str, senator_col: str | None):
    """
    Collapse multiple rows per state into exactly two columns v1, v2.
    If only one vote exists (vacancy), pad with None.
    """
    # normalize votes
    df = df.copy()

    # Order within state
    if senator_col and senator_col in df.columns:
        df = df.sort_values([state_col, senator_col])
    else:
        # preserve input order within state as a fallback
        df["_ord"] = df.groupby(state_col).cumcount()
        df = df.sort_values([state_col, "_ord"])

    # roll up to two votes
    agg = (df.groupby(state_col)[vote_col]
             .apply(list)
             .apply(lambda lst: (lst + [None, None])[:2])  # pad to length 2
             .apply(pd.Series)
             .rename(columns={0: "v1", 1: "v2"})
             .reset_index())
    return agg

def render_map_senate(
    gdf: gpd.GeoDataFrame,
    title: str = "Senate Vote",
    state_col: str = "STUSPS",
    vote_col: str = "vote",
    senator_col: str | None = None,
    outfile: str | None = None,
    show: bool = False
):
    """
    Expects gdf to include one or two rows per state with a 'vote' column.
    Will collapse to a single centroid per state and plot two colored squares.
    """
    # keep one geometry per state, drop duplicate geometries from the join
    base = (gdf[[state_col, "geometry"]]
            .drop_duplicates(subset=[state_col])
            .reset_index(drop=True))

    # derive v1, v2 per state from the possibly duplicated rows
    votes2 = _two_votes_per_state(gdf[[state_col, vote_col] + ([senator_col] if senator_col and senator_col in gdf.columns else [])],
                                  state_col=state_col, vote_col=vote_col, senator_col=senator_col)

    # join back to one-geometry-per-state
    states = base.merge(votes2, on=state_col, how="left")

    # project to Albers before centroids and offsets
    states = _to_albers(states)
    states["cx"] = states.geometry.centroid.x
    states["cy"] = states.geometry.centroid.y

    # choose offsets relative to map width
    minx, miny, maxx, maxy = states.total_bounds
    dx = (maxx - minx) * 0.018  # left/right spacing
    size = max((maxx - minx), (maxy - miny)) * 0.00008  # scale-ish; gets converted to points via 's'

    def c(v):
        return VOTE_PALETTE.get(_normalize_vote(v), "#bbbbbb")

    fig, ax = plt.subplots(figsize=(11, 7))
    # base fill and outline
    states.plot(ax=ax, facecolor="#f8f8f8", edgecolor="#444444", linewidth=0.6, zorder=1)

    # left and right squares
    ax.scatter(states["cx"] - dx, states["cy"], s=400, marker="s", zorder=5, c=states["v1"].map(c))
    ax.scatter(states["cx"] + dx, states["cy"], s=400, marker="s", zorder=5, c=states["v2"].map(c))

    # legend
    present_values = [v for v in ["Yea", "Nay", "Present", "Not Voting"]
                      if v in set(states[["v1","v2"]].stack().dropna().map(_normalize_vote).unique())]
    handles = [mpatches.Patch(color=VOTE_PALETTE[v], label=v) for v in present_values]
    if handles:
        ax.legend(handles=handles, title="Vote", loc="lower left", frameon=True)

    ax.set_title(title)
    ax.set_axis_off()
    fig.tight_layout()

    if outfile:
        fig.savefig(outfile, dpi=220, bbox_inches="tight")
        print(f"Saved {outfile} (backend {matplotlib.get_backend()})")
    if show:
        plt.show()

    return fig, ax
