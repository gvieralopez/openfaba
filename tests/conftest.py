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


@pytest.fixture
def fake_source_dir(tmp_path: Path) -> Path:
    d = tmp_path / "source"
    d.mkdir()
    return d


@pytest.fixture
def fake_faba_library(tmp_path: Path) -> Path:
    d = tmp_path / "MKI01"
    d.mkdir()
    return d


@pytest.fixture
def fake_mp3_library(tmp_path: Path) -> Path:
    d = tmp_path / "mp3"
    d.mkdir()
    return d
