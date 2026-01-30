from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def mki_library(fixtures_dir: Path) -> Path:
    """Return the path to the MKI01 fixture library."""
    return fixtures_dir / "MKI01"
