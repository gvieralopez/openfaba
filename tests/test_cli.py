from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch
from typer.testing import CliRunner

from openfaba.cli import app

runner = CliRunner()

## `normalize_figure_id`


@pytest.mark.parametrize(
    "value,expected",
    [
        ("1", "0001"),
        ("12", "0012"),
        ("1234", "1234"),
        ("0001", "0001"),
        ("12345", None),
        ("abcd", None),
        ("", None),
    ],
)
def test_normalize_figure_id(value: str, expected: str | None) -> None:
    from openfaba.cli import normalize_figure_id

    assert normalize_figure_id(value) == expected


## `insert`


def test_insert_success(
    monkeypatch: MonkeyPatch, fake_source_dir: Path, fake_faba_library: Path
) -> None:
    monkeypatch.setattr(
        "openfaba.cli.collect_all_mp3_files_in_folder", lambda _: [Path("a.mp3"), Path("b.mp3")]
    )

    obfuscate = Mock()
    monkeypatch.setattr("openfaba.cli.obfuscate_figure_mp3_files", obfuscate)

    result = runner.invoke(
        app,
        [
            "insert",
            "--figure-id",
            "1",
            "--source",
            str(fake_source_dir),
            "--faba-library",
            str(fake_faba_library),
        ],
    )

    assert result.exit_code == 0
    assert "Inserted figure K0001. Added 2 tracks." in result.stdout
    obfuscate.assert_called_once()


### Invalid figure id


def test_insert_invalid_figure_id() -> None:
    result = runner.invoke(
        app,
        [
            "insert",
            "--figure-id",
            "abcd",
            "--source",
            ".",
            "--faba-library",
            ".",
        ],
    )

    assert result.exit_code != 0
    assert "figure-id must be a 4-digit number" in result.stdout


## `extend`


def test_extend_success(
    monkeypatch: MonkeyPatch, fake_source_dir: Path, fake_faba_library: Path
) -> None:
    figure_dir = fake_faba_library / "K0001"
    figure_dir.mkdir()

    monkeypatch.setattr("openfaba.cli.collect_all_mp3_files_in_folder", lambda _: [Path("a.mp3")])

    obfuscate = Mock()
    monkeypatch.setattr("openfaba.cli.obfuscate_figure_mp3_files", obfuscate)

    result = runner.invoke(
        app,
        [
            "extend",
            "--figure-id",
            "1",
            "--source",
            str(fake_source_dir),
            "--faba-library",
            str(fake_faba_library),
        ],
    )

    assert result.exit_code == 0
    assert "Extended figure K0001. Appended 1 tracks." in result.stdout
    obfuscate.assert_called_once()


### Missing figure


def test_extend_missing_figure(fake_source_dir: Path, fake_faba_library: Path) -> None:
    result = runner.invoke(
        app,
        [
            "extend",
            "--figure-id",
            "1",
            "--source",
            str(fake_source_dir),
            "--faba-library",
            str(fake_faba_library),
        ],
    )

    assert result.exit_code == 1
    assert "does not exist" in result.stdout


## `replace`


def test_replace_removes_existing(
    monkeypatch: MonkeyPatch, fake_source_dir: Path, fake_faba_library: Path
) -> None:
    fig = fake_faba_library / "K0001"
    fig.mkdir()
    (fig / "old_file").touch()

    monkeypatch.setattr("openfaba.cli.collect_all_mp3_files_in_folder", lambda _: [Path("new.mp3")])

    obfuscate = Mock()
    monkeypatch.setattr("openfaba.cli.obfuscate_figure_mp3_files", obfuscate)

    result = runner.invoke(
        app,
        [
            "replace",
            "--figure-id",
            "1",
            "--source",
            str(fake_source_dir),
            "--faba-library",
            str(fake_faba_library),
        ],
    )

    assert result.exit_code == 0
    assert "Replaced figure K0001. Created with 1 tracks." in result.stdout
    assert not fig.exists() or fig.is_dir()


## `extract`


def test_extract_success(monkeypatch: MonkeyPatch, fake_faba_library: Path, tmp_path: Path) -> None:
    monkeypatch.setattr("openfaba.cli.deobfuscate_figure_mki_files", lambda *_: 3)

    output = tmp_path / "out"

    result = runner.invoke(
        app,
        [
            "extract",
            "--figure-id",
            "1",
            "--faba-library",
            str(fake_faba_library),
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0
    assert "Extracted figure K0001. Converted 3 files." in result.stdout


## `obfuscate`


def test_obfuscate_library(
    monkeypatch: MonkeyPatch, fake_mp3_library: Path, fake_faba_library: Path
) -> None:
    monkeypatch.setattr("openfaba.cli.obfuscate_mp3_library", lambda *_: 5)

    result = runner.invoke(
        app,
        [
            "obfuscate",
            "--mp3-library",
            str(fake_mp3_library),
            "--faba-library",
            str(fake_faba_library),
        ],
    )

    assert result.exit_code == 0
    assert "Converted 5 files" in result.stdout


## `deobfuscate`


def test_deobfuscate_library(
    monkeypatch: MonkeyPatch, fake_mp3_library: Path, fake_faba_library: Path
) -> None:
    monkeypatch.setattr("openfaba.cli.deobfuscate_mki_library", lambda *_: 2)

    result = runner.invoke(
        app,
        [
            "deobfuscate",
            "--faba-library",
            str(fake_faba_library),
            "--mp3-library",
            str(fake_mp3_library),
        ],
    )

    assert result.exit_code == 0
    assert "Converted 2 files" in result.stdout
