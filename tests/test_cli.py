import sys
import pytest
import matplotlib
matplotlib.use("Agg")

from src.cli import main

@pytest.mark.smoke
def test_cli_senate_smoke(monkeypatch):
    testargs = [
        "cli.py",
        "--chamber", "senate",
        "--congress", "117",
        "--session", "2",
        "--roll", "45",
        "--background", "white",
    ]
    monkeypatch.setattr(sys, 'argv', testargs)
    try:
        main()
    except Exception as e:
        pytest.fail(f"CLI senate smoke test failed: {e}")

@pytest.mark.smoke
def test_cli_house_smoke(monkeypatch):
    testargs = [
        "cli.py",
        "--chamber", "house",
        "--congress", "117",
        "--session", "2",
        "--roll", "45",
        "--background", "white",
    ]
    monkeypatch.setattr(sys, 'argv', testargs)
    try:
        main()
    except Exception as e:
        pytest.fail(f"CLI house smoke test failed: {e}")