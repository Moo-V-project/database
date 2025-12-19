from pathlib import Path
from glob import glob

import pytest


BASE_CSV_PATH = Path(__file__).parent.parent / "fixtures" / "csv"


@pytest.fixture(params=glob(f"{BASE_CSV_PATH}/invalid/*"))
def csv_dir_invalid(request) -> Path:
    return Path(request.param)


@pytest.fixture
def csv_dir_valid() -> Path:
    return BASE_CSV_PATH / "valid"


@pytest.fixture
def csv_dir_missing_file() -> Path:
    return BASE_CSV_PATH / "missing_file"
