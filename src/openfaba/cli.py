import logging
from pathlib import Path

import typer
from typer import Typer

from openfaba.media import deobfuscate_mki_library, obfuscate_mp3_library

logger = logging.getLogger(__name__)
app = Typer(help="Obfuscate/Deobfuscate Faba box MP3s")


@app.command()
def encrypt(
    source_folder: Path = typer.Option(
        ...,
        "--source-folder",
        "-s",
        help="Folder with MP3 files to process.",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    target_folder: Path = typer.Option(
        ...,
        "--target-folder",
        "-t",
        help="Folder where generated Faba .MKI files will be stored. "
        "Subfolder for the figure will be created.",
        file_okay=False,
        dir_okay=True,
    ),
    # figure_id: str = typer.Option(
    #     "0000", "--figure-id", "-f", help="Faba NFC chip identifier (4 digit number 0001-9999)"
    # )
) -> None:
    """Encrypt MP3 files for Faba box."""
    if not source_folder.is_dir():
        typer.echo(
            f"Error: Source folder '{source_folder}' does not exist or is not a directory.",
            err=True,
        )
        raise typer.Exit(code=1)

    obfuscated = obfuscate_mp3_library(source_folder, target_folder)
    if obfuscated == 0:
        typer.echo("No MP3 files found in the source folder.", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Processing complete. Converted {obfuscated} files.")


@app.command()
def decrypt(
    source_folder: Path = typer.Option(
        ...,
        "--source-folder",
        "-s",
        help="Folder with MKI files to process. Supports recursion.",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    target_folder: Path = typer.Option(
        ...,
        "--target-folder",
        "-t",
        help="Folder for decrypted MP3 files.",
        file_okay=False,
        dir_okay=True,
    ),
) -> None:
    """Decrypt MKI files from Faba box."""
    if not source_folder.is_dir():
        typer.echo(
            f"Error: Source folder '{source_folder}' does not exist or is not a directory.",
            err=True,
        )
        raise typer.Exit(code=1)

    deobfuscated = deobfuscate_mki_library(source_folder, target_folder)
    if deobfuscated == 0:
        typer.echo("No MKI files found in the source folder.", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Processing complete. Converted {deobfuscated} files.")
