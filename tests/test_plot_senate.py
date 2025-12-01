import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.maps.plot_senate import _votes_by_state, render_map_senate
import pandas as pd

def _assert_render_ok(df, title):
    fig, ax = render_map_senate(df, background="white", title=title)
    # Ensure we can draw without raising
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    assert buf.getbuffer().nbytes > 0

def test_render_states_map():
    data = {
        'STUSPS': ['CA', 'CA', 'TX', 'TX', 'FL', 'FL'],
        'vote': ['Yea', 'Nay', 'Yea', 'Yea', 'Nay', None]
    }
    df = pd.DataFrame(data)
    _assert_render_ok(df, title="Senate Votes Test")

def test_rejects_non_dataframe():
    df = "There once was a man from nantucket... it goes on, I dont know the rest of the rhyme."
    try:
        render_map_senate(df, background="white")
        assert False, "Expected TypeError for non-DataFrame"
    except TypeError:
        pass

def test_votes_by_state():
    data = {
        'STUSPS': ['NY', 'NY', 'CA', 'CA', 'TX'],
        'vote': ['Yea', 'Nay', 'Nay', None, 'Yea']
    }
    df = pd.DataFrame(data)
    votes = _votes_by_state(df, vote_col='vote')
    assert votes == {
        'NY': ['Yea', 'Nay'],
        'CA': ['Nay', 'Not Voting'],
        'TX': ['Yea', 'Not Voting']
    }