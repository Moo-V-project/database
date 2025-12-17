from pathlib import Path
import pytest


@pytest.fixture
def csv_fixtures_dir() -> Path:
    return Path(__file__).parent.parent / "fixtures" / "csv"
