# src/maps/plot_senate.py
import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import geopandas as gpd

# Normalize vote labels coming from the Senate XML
VOTE_NORMALIZE = {
    "Aye": "Yea", "Yes": "Yea", "Yea": "Yea",
    "No": "Nay", "Nay": "Nay",
    "Present": "Present",
    "Not Voting": "Not Voting", "NotVoting": "Not Voting", "NV": "Not Voting",
    "Excused": "Not Voting", "Absent": "Not Voting", None: "Not Voting",
}

def _normalize_vote(v):
    if v is None:
        return "Not Voting"
    v = str(v).strip()
    return VOTE_NORMALIZE.get(v, v)

# Keep colors consistent with the project palette (same as House)
# Green, Red, Orange, Gray
VOTE_PALETTE = {
    "Yea": "#2ca02c",
    "Nay": "#d62728",
    "Present": "#ff7f0e",
    "Not Voting": "#7f7f7f",
}

# A standard 50–state tile layout (similar to FiveThirtyEight/R-tilemap style).
# row 0 is top. (row, col) positions form a contiguous USA-ish block plus AK, HI.
TILE_POS = {
    # Far outliers
    "AK": (1, 0), "HI": (6, 0),
    # West to east main body
    "WA": (2, 1), "ID": (2, 2), "MT": (2, 3), "ND": (2, 4), "MN": (2, 5), "WI": (1, 6), "MI": (2, 7),
    "OR": (3, 1), "NV": (3, 2), "WY": (3, 3), "SD": (3, 4), "IA": (3, 5), "IL": (2, 6), "IN": (3, 6), "OH": (3, 7), "PA": (3, 8),
    "CA": (4, 1), "UT": (4, 2), "CO": (4, 3), "NE": (4, 4), "MO": (4, 5), "KY": (4, 6), "WV": (4, 7), "VA": (4, 8), "MD": (4, 9), "DE": (4,10),
    "AZ": (5, 2), "NM": (5, 3), "KS": (5, 4), "AR": (5, 5), "TN": (5, 6), "NC": (5, 7), "SC": (5, 8),
    "OK": (6, 4), "LA": (6, 5), "MS": (6, 6), "AL": (6, 7), "GA": (6, 8), "FL": (7, 9), "TX": (7, 4),
    "NY": (2, 9), "NJ": (3, 9), "CT": (3, 10), "RI": (2, 10), "MA": (2, 11), "VT": (1, 10), "NH": (1,11), "ME": (0,11),
}

# If a state isn’t in TILE_POS, we’ll place it in a simple spillover row to avoid crashes.

def _votes_by_state(joined: gpd.GeoDataFrame, vote_col: str) -> dict:
    """
    Input: GeoDataFrame after join (two rows per state for Senate).
    Output: { 'STUSPS' -> [vote_for_sen1, vote_for_sen2] }
    Ordering is deterministic but not seniority: preserve XML order as merged.
    If fewer than two rows are present, pad with 'Not Voting'.
    """
    if "STUSPS" not in joined.columns or vote_col not in joined.columns:
        raise ValueError("Expected columns 'STUSPS' and vote column in joined data.")

    # Keep insertion order from the source (stable groupby with cumcount later)
    joined = joined[["STUSPS", vote_col]].copy()
    # Normalize vote labels
    joined[vote_col] = joined[vote_col].map(_normalize_vote)

    votes = {}
    for st, grp in joined.groupby("STUSPS", sort=False):
        vals = [v for v in grp[vote_col].tolist() if pd.notna(v)]
        # pad/truncate to exactly two entries
        vals = (vals + ["Not Voting", "Not Voting"])[:2]
        votes[st] = vals
    return votes

def _tile_bbox(tile_size=1.0, gap=0.08):
    w = tile_size
    h = tile_size
    inner_gap = gap
    return w, h, inner_gap

def render_map_senate(
    gdf: gpd.GeoDataFrame,
    title: str = "Senate",
    vote_col: str = "vote",
    outfile: str | None = None,
    show: bool = False,
):
    """
    Render a 50-state tile grid for Senate votes (two votes per state).
    House plotting is defined elsewhere and is not modified here.
    """
    if not isinstance(gdf, gpd.GeoDataFrame):
        raise TypeError("render_map_senate expects a GeoDataFrame after join_votes(...).")

    # Build state -> [vote1, vote2] map
    state_votes = _votes_by_state(gdf, vote_col)

    # Figure & axes (use default matplotlib size unless caller sets rcparams)
    fig, ax = plt.subplots(figsize=(12, 8))  # "default" feel; close to your current output
    ax.set_axis_off()

    # geometry not used for placement; we draw a grid
    tile_w, tile_h, inner_gap = _tile_bbox(tile_size=1.0, gap=0.08)

    # Track encountered states to drop exact duplicates
    plotted = set()

    # Build a reverse lookup for spillover placement if a state isn’t in TILE_POS
    spill_row = 8
    spill_col = 2

    # Draw tiles
    for st in sorted(state_votes.keys(), key=lambda s: (TILE_POS.get(s, (99, 99))[0], TILE_POS.get(s, (99, 99))[1], s)):
        if st in plotted:
            continue
        plotted.add(st)

        r, c = TILE_POS.get(st, (spill_row, spill_col))
        if st not in TILE_POS:
            spill_col += 1  # move along the spill row

        # Outer tile (background)
        x0 = c * (tile_w + 0.15)
        y0 = -r * (tile_h + 0.15)

        # Two inner rectangles: left & right
        votes = state_votes.get(st, ["Not Voting", "Not Voting"])
        left_col  = VOTE_PALETTE.get(_normalize_vote(votes[0]), VOTE_PALETTE["Not Voting"])
        right_col = VOTE_PALETTE.get(_normalize_vote(votes[1]), VOTE_PALETTE["Not Voting"])

        # Outer border tile
        outer = plt.Rectangle((x0, y0), tile_w, tile_h, linewidth=0.6, edgecolor="white", facecolor="#4e7890")
        ax.add_patch(outer)

        # Inner two blocks
        inner_w = (tile_w - inner_gap) / 2.0
        inner_h = tile_h - inner_gap
        inner_y = y0 + inner_gap / 2.0
        left_x  = x0 + inner_gap / 2.0
        right_x = x0 + inner_gap / 2.0 + inner_w + inner_gap / 2.0

        ax.add_patch(plt.Rectangle((left_x,  inner_y), inner_w, inner_h, facecolor=left_col,  edgecolor="none"))
        ax.add_patch(plt.Rectangle((right_x, inner_y), inner_w, inner_h, facecolor=right_col, edgecolor="none"))

        # State label
        ax.text(x0 + tile_w / 2.0, y0 + tile_h / 2.0, st,
                ha="center", va="center", fontsize=9, color="white", weight="bold")
    
    ax.set_xlim(-0.5, 14.5)
    ax.set_ylim(-9.5, 1.5)
    ax.set_aspect("equal", adjustable="box")

    # Legend (only include categories used)
    used_cats = pd.unique([_normalize_vote(v) for vs in state_votes.values() for v in vs])
    handles = []
    for cat in ["Yea", "Nay", "Present", "Not Voting"]:
        if cat in used_cats:
            handles.append(mpatches.Patch(color=VOTE_PALETTE[cat], label=cat))
    if handles:
        ax.legend(handles=handles, title="Vote", loc="lower left", frameon=True)

    ax.set_title(title)
    fig.tight_layout()

    if outfile:
        fig.savefig(outfile, dpi=220, bbox_inches="tight")
        print(f"Saved {outfile} (backend {matplotlib.get_backend()})")
    if show:
        plt.show()

    return fig, ax
