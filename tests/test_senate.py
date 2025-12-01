from src.senate import _parse_senate_members, SenateSource

def test_parse_senate_members():
    xml_content = """
    <root>
        <members>
            <member>
                <state>CA</state>
                <vote_cast>Yea</vote_cast>
            </member>
            <member>
                <state>TX</state>
                <vote_cast>Nay</vote_cast>
            </member>
            <member>
                <state>FL</state>
                <vote_cast></vote_cast>
            </member>
        </members>
    </root>
    """
    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml_content)
    df = _parse_senate_members(root)
    
    assert len(df) == 3
    assert df.iloc[0]['geoid'] == 'CA'
    assert df.iloc[0]['vote'] == 'Yea'
    assert df.iloc[1]['geoid'] == 'TX'
    assert df.iloc[1]['vote'] == 'Nay'
    assert df.iloc[2]['geoid'] == 'FL'
    assert df.iloc[2]['vote'] == 'Not Voting'

def test_senate_source_fetch(monkeypatch):
    class MockResponse:
        def __init__(self, content):
            self.content = content
        def raise_for_status(self):
            pass

    def mock_get(url, timeout):
        xml_content = """
        <root>
            <members>
                <member>
                    <state>NY</state>
                    <vote_cast>Yea</vote_cast>
                </member>
                <member>
                    <state>NJ</state>
                    <vote_cast>Nay</vote_cast>
                </member>
            </members>
        </root>
        """
        return MockResponse(xml_content.encode('utf-8'))

    monkeypatch.setattr("requests.get", mock_get)

    source = SenateSource()
    df = source.fetch(congress=117, session=2, roll=45)

    assert len(df) == 2
    assert df.iloc[0]['geoid'] == 'NY'
    assert df.iloc[0]['vote'] == 'Yea'
    assert df.iloc[1]['geoid'] == 'NJ'
    assert df.iloc[1]['vote'] == 'Nay'