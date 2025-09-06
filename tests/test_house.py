from src.house import HouseSource, _congress_to_year, _house_url, _parse_house_members
import responses
import pandas as pd
import xml.etree.ElementTree as ET

def test_congress_to_year():
    assert _congress_to_year(1) == 1789
    assert _congress_to_year(117) == 2021
    assert _congress_to_year(118) == 2023

def test_house_url():
    assert _house_url(2021, 45) == (
        "https://clerk.house.gov/evs/2021/roll045.xml"
    )
    assert _house_url(2023, 123) == (
        "https://clerk.house.gov/evs/2023/roll123.xml"
    )

@responses.activate
def test_fetch_parse_house_members():
    url = "https://clerk.house.gov/evs/2021/roll045.xml"

    responses.add(responses.HEAD, url, status=200)

    xml = b"""
    <rollcall-vote>
      <vote-data>
        <recorded-vote>
          <legislator state="CA" district="12"/>
          <vote>Yea</vote>
        </recorded-vote>
        <recorded-vote>
          <legislator state="TX" district="07"/>
          <vote>Nay</vote>
        </recorded-vote>
      </vote-data>
    </rollcall-vote>
    """
    responses.add(responses.GET, url, body=xml, status=200)

    df = HouseSource().fetch(117, 45)  # if your fetch signature is (congress, roll)
    assert set(df.columns) == {"geoid", "vote"}
    assert len(df) == 2
    assert set(df["geoid"]) == {"CA-12", "TX-07"}
    assert set(df["vote"]) == {"Yea", "Nay"}