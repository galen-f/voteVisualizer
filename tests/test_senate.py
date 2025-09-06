from src.senate import SenateSource, _senate_url
import responses
import pandas as pd

def test_senate_url():
    assert _senate_url(117, 1, 45) == (
        "https://www.senate.gov/legislative/LIS/roll_call_votes/"
        "vote1171/vote_117_1_00045.xml"
    )
    assert _senate_url(116, 2, 123) == (
        "https://www.senate.gov/legislative/LIS/roll_call_votes/"
        "vote1162/vote_116_2_00123.xml"
    )

@responses.activate
def test_fetch_parses_members():
    url = _senate_url(117,1,45)
    xml = b"""
    <roll_call_vote>
      <members>
        <member><state>CA</state><vote_cast>Yea</vote_cast></member>
        <member><state>CA</state><vote_cast>Nay</vote_cast></member>
      </members>
    </roll_call_vote>"""
    responses.add(responses.GET, url, body=xml, status=200)
    df = SenateSource().fetch(117,1,45)
    assert set(df.columns) == {"geoid","vote"}
    assert len(df) == 2