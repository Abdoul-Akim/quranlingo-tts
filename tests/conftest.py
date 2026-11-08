# Lets the tests import the shared tools (tools/*.py) by name.
# Run all tests from the TTS folder:  uv run --project analysis python -m pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import pytest


@pytest.fixture(autouse=True)
def no_owner_shortlist(monkeypatch):
    # Tests use made-up takes, so the owner's real shortlist must not apply unless a test sets one.
    import make_round
    import rank_takes
    monkeypatch.setattr(make_round, "OWNER_SHORTLIST", {})
    monkeypatch.setattr(rank_takes, "OWNER_SHORTLIST", {})
