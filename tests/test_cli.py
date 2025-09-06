import sys
import pytest
import matplotlib
matplotlib.use("Agg")

from src.cli import main

@pytest.mark.smoke
def test_cli_senate_smoke(monkeypatch):
    """End-to-end CLI smoke for Senate path using a fake source that returns 'state' keys."""
    class FakeSenateSource:
        def fetch(self, congress: int, session: int, roll: int):
            import pandas as pd
            # Provide 'state' to satisfy join function expectations in refactor
            return pd.DataFrame([
                {"state": "CA", "vote": "Yea"},
                {"state": "TX", "vote": "Nay"},
            ])

    import src.cli as cli_mod
    # Force the CLI to use our fake source
    monkeypatch.setattr(cli_mod, "present_senate_data", lambda: FakeSenateSource())

    argv = ["prog", "--chamber", "senate", "--congress", "117", "--session", "1", "--roll", "45", "--no-show"]
    monkeypatch.setenv("MPLBACKEND", "Agg")
    monkeypatch.setattr(sys, "argv", argv)
    main()  # should not raise

@pytest.mark.smoke
def test_cli_house_smoke(monkeypatch):
    """End-to-end CLI smoke for House path using a fake source that returns district 'geoid's."""
    class FakeHouseSource:
        def fetch(self, congress: int, session: int, roll: int):
            import pandas as pd
            return pd.DataFrame([
                {"geoid": "CA-12", "vote": "Yea"},
                {"geoid": "TX-07", "vote": "Nay"},
            ])

    import src.cli as cli_mod
    monkeypatch.setattr(cli_mod, "present_house_data", lambda: FakeHouseSource())

    argv = ["prog", "--chamber", "house", "--congress", "117", "--session", "1", "--roll", "12", "--no-show"]
    monkeypatch.setenv("MPLBACKEND", "Agg")
    monkeypatch.setattr(sys, "argv", argv)
    main()  # should not raise
