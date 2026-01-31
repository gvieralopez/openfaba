import logging
import shutil
from pathlib import Path

import typer
from typer import Typer

from openfaba.io import collect_all_mp3_files_in_folder
from openfaba.media import (
    deobfuscate_figure_mki_files,
    deobfuscate_mki_library,
    obfuscate_figure_mp3_files,
    obfuscate_mp3_library,
)

logger = logging.getLogger(__name__)
app = Typer(help="Create/Manage FABA figures and libraries")


def normalize_figure_id(figure_id: str) -> str | None:
    return f"{int(figure_id):04d}" if (figure_id.isdigit() and len(figure_id) <= 4) else None


@app.command()
def insert(
    figure_id: str = typer.Option(..., "--figure-id", "-f", help="Figure ID (4 digits)"),
    source: Path = typer.Option(..., "--source", "-s", exists=True, file_okay=False, dir_okay=True),
    faba_library: Path = typer.Option(
        ..., "--faba-library", "-b", exists=True, file_okay=False, dir_okay=True
    ),
) -> None:
    """Create a new FABA figure from a folder of MP3 files. Fails if figure exists."""

    if not (fid := normalize_figure_id(figure_id)):
        raise typer.BadParameter("figure-id must be a 4-digit number")

    figure_path = faba_library / f"K{fid}"
    if figure_path.exists():
        if not figure_path.is_dir():
            typer.echo(f"Error: Path for Figure K{fid} already exists as a file.", err=True)
            raise typer.Exit(code=1)
        elif len(list(figure_path.iterdir())) != 0:
            typer.echo(f"Error: Figure K{fid} already exists as a not empty folder.", err=True)
            raise typer.Exit(code=1)

    if not (mp3_files := collect_all_mp3_files_in_folder(source)):
        typer.echo("No MP3 files found in the source folder.", err=True)
        raise typer.Exit(code=1)

    obfuscate_figure_mp3_files(fid, mp3_files, faba_library)
    typer.echo(f"Inserted figure K{fid}. Added {len(mp3_files)} tracks.")


@app.command()
def extend(
    figure_id: str = typer.Option(..., "--figure-id", "-f", help="Figure ID (4 digits)"),
    source: Path = typer.Option(..., "--source", "-s", exists=True, file_okay=False, dir_okay=True),
    faba_library: Path = typer.Option(
        ..., "--faba-library", "-b", exists=True, file_okay=False, dir_okay=True
    ),
) -> None:
    """Append MP3 files to an existing figure. Does not overwrite existing tracks."""

    if not (fid := normalize_figure_id(figure_id)):
        raise typer.BadParameter("figure-id must be a 4-digit number")

    figure_path = faba_library / f"K{fid}"
    if not figure_path.exists():
        typer.echo(f"Error: Figure K{fid} does not exist in the library.", err=True)
        raise typer.Exit(code=1)

    if not (mp3_files := collect_all_mp3_files_in_folder(source)):
        typer.echo("No MP3 files found in the source folder.", err=True)
        raise typer.Exit(code=1)

    obfuscate_figure_mp3_files(fid, mp3_files, faba_library, append=True)
    added = len(mp3_files)
    if added == 0:
        typer.echo("No files were appended.", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Extended figure K{fid}. Appended {added} tracks.")


@app.command()
def replace(
    figure_id: str = typer.Option(..., "--figure-id", "-f", help="Figure ID (4 digits)"),
    source: Path = typer.Option(..., "--source", "-s", exists=True, file_okay=False, dir_okay=True),
    faba_library: Path = typer.Option(
        ..., "--faba-library", "-b", exists=True, file_okay=False, dir_okay=True
    ),
) -> None:
    """Delete an existing figure and recreate it from MP3 files."""

    if not (fid := normalize_figure_id(figure_id)):
        raise typer.BadParameter("figure-id must be a 4-digit number")

    figure_path = faba_library / f"K{fid}"
    if figure_path.exists():
        try:
            shutil.rmtree(figure_path)
        except Exception as exc:
            typer.echo(f"Error removing existing figure: {exc}", err=True)
            raise typer.Exit(code=1) from exc

    if not (mp3_files := collect_all_mp3_files_in_folder(source)):
        typer.echo("No MP3 files found in the source folder.", err=True)
        raise typer.Exit(code=1)

    obfuscate_figure_mp3_files(fid, mp3_files, faba_library)
    typer.echo(f"Replaced figure K{fid}. Created with {len(mp3_files)} tracks.")


@app.command()
def extract(
    figure_id: str = typer.Option(..., "--figure-id", "-f", help="Figure ID (4 digits)"),
    faba_library: Path = typer.Option(
        ..., "--faba-library", "-b", exists=True, file_okay=False, dir_okay=True
    ),
    output: Path = typer.Option(..., "--output", "-o", file_okay=False, dir_okay=True),
) -> None:
    """Extract a single figure from a FABA library into MP3 files."""

    if not (fid := normalize_figure_id(figure_id)):
        raise typer.BadParameter("figure-id must be a 4-digit number")
    output.mkdir(parents=True, exist_ok=True)

    converted = deobfuscate_figure_mki_files(fid, faba_library, output)
    if converted == 0:
        typer.echo(f"No MKI files found for figure K{fid}.", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Extracted figure K{fid}. Converted {converted} files.")


@app.command()
def obfuscate(
    mp3_library: Path = typer.Option(
        ..., "--mp3-library", "-m", exists=True, file_okay=False, dir_okay=True
    ),
    faba_library: Path = typer.Option(
        ..., "--faba-library", "-b", exists=True, file_okay=False, dir_okay=True
    ),
) -> None:
    """Obfuscate an entire MP3 library into a FABA MKI library."""
    converted = obfuscate_mp3_library(mp3_library, faba_library)
    if converted == 0:
        typer.echo("No MP3 files found in the source library.", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Obfuscated library. Converted {converted} files.")


@app.command()
def deobfuscate(
    faba_library: Path = typer.Option(
        ..., "--faba-library", "-b", exists=True, file_okay=False, dir_okay=True
    ),
    mp3_library: Path = typer.Option(..., "--mp3-library", "-m", file_okay=False, dir_okay=True),
) -> None:
    """Deobfuscate an entire FABA MKI library back into MP3 files."""
    mp3_library.mkdir(parents=True, exist_ok=True)

    converted = deobfuscate_mki_library(faba_library, mp3_library)
    if converted == 0:
        typer.echo("No MKI files found in the FABA library.", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Deobfuscated library. Converted {converted} files.")
