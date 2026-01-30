import logging
import re
import shutil
from pathlib import Path

import mutagen
import typer
from typer import Typer

from openfaba.io import clear_tags_and_set_title, convert_mki_to_mp3, convert_mp3_to_mki
from openfaba.utils import id3header_constructor_monkeypatch

logger = logging.getLogger(__name__)
app = Typer(help="Encrypt/Decrypt Faba box MP3s")


def encrypt_command(
    source_folder: Path, target_folder: Path, figure_id: str = "0000", extract_figure: bool = False
) -> None:
    """Encrypt MP3 files for Faba box."""
    # monkeypatch out exceptions on invalid ID3 headers
    mutagen.id3._tags.ID3Header.__init__ = id3header_constructor_monkeypatch

    count = 0
    mp3_files: dict[str, list[Path]] = {}

    if extract_figure:
        for root, _, filenames in source_folder.walk():
            for filename in filenames:
                full_path = Path(root) / filename
                if filename.lower().endswith(".mp3"):
                    # Extract figure ID from directory name (K####)
                    match = re.search(r"[\\/]K(\d{4})$", str(root))
                    if match:
                        mp3_files.setdefault(match.group(1), []).append(full_path)
                        count += 1
    else:
        if not re.match(r"^\d{4}$", figure_id):
            typer.echo("Error: Figure ID must be exactly 4 digits.", err=True)
            raise typer.Exit(code=1)

        for root, _, filenames in source_folder.walk():
            for filename in filenames:
                full_path = Path(root) / filename
                if filename.lower().endswith(".mp3"):
                    mp3_files.setdefault(figure_id, []).append(full_path)
                    count += 1

    if count == 0:
        typer.echo("No MP3 files found in the source folder.", err=True)
        raise typer.Exit(code=1)

    iterator = 1
    for figure in mp3_files:
        figure_path = target_folder / f"K{figure}"
        figure_path.mkdir(exist_ok=True, parents=True)

        for filenum, file in enumerate(sorted(mp3_files[figure]), start=1):
            typer.echo(f"=========================[{iterator}/{count}]")
            typer.echo(f"Processing {file}...")

            filenum_str = f"{filenum:02d}"
            new_title = f"K{figure}CP{filenum_str}"
            target_file = figure_path / f"CP{filenum_str}"

            shutil.copy(file, target_file)
            clear_tags_and_set_title(target_file, new_title)

            encrypted_file = target_file.with_suffix(".MKI")
            convert_mp3_to_mki(target_file, encrypted_file)
            target_file.unlink()

            iterator += 1

    typer.echo(
        f"Processing complete. Copy the files from '{target_folder}' directory to your Faba box."
    )


def decrypt_command(source_folder: Path, target_folder: Path) -> None:
    """Decrypt MKI files from Faba box."""
    count = 0
    mki_files: dict[str, list[str]] = {}

    for root, _, filenames in source_folder.walk():
        for filename in filenames:
            if filename.lower().endswith(".mki"):
                rel_path = Path(root).relative_to(source_folder)
                mki_files.setdefault(str(rel_path), []).append(filename)
                count += 1

    if count == 0:
        typer.echo("No MKI files found in the source folder.", err=True)
        raise typer.Exit(code=1)

    iterator = 1
    for subdir in mki_files:
        subdir_path = target_folder / subdir
        subdir_path.mkdir(parents=True, exist_ok=True)

        for file in mki_files[subdir]:
            typer.echo(f"=========================[{iterator}/{count}]")
            typer.echo(f"Processing {Path(subdir) / file}...")

            source_file = source_folder / subdir / file
            target_file = target_folder / subdir / file

            if target_file.suffix.lower() == ".mki":
                target_file = target_file.with_suffix(".mp3")

            convert_mki_to_mp3(source_file, target_file)
            iterator += 1

    typer.echo("Processing complete.")


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
    figure_id: str = typer.Option(
        "0000", "--figure-id", "-f", help="Faba NFC chip identifier (4 digit number 0001-9999)"
    ),
    extract_figure: bool = typer.Option(
        False,
        "--extract-figure",
        "-x",
        help="Get figure ID from directory name (MP3 files must be in folders named K0001-K9999)",
    ),
) -> None:
    """Encrypt MP3 files for Faba box."""
    if not source_folder.is_dir():
        typer.echo(
            f"Error: Source folder '{source_folder}' does not exist or is not a directory.",
            err=True,
        )
        raise typer.Exit(code=1)

    encrypt_command(source_folder, target_folder, figure_id, extract_figure)


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

    decrypt_command(source_folder, target_folder)


def main():
    app()


if __name__ == "__main__":
    main()
