import logging
import re
import shutil
import tempfile
from collections import defaultdict
from pathlib import Path

from openfaba.io import clear_tags_and_set_title, convert_mki_to_mp3, convert_mp3_to_mki

logger = logging.getLogger(__name__)


def obfuscate_figure_mp3_files(
    figure_id: str, source_mp3_files: list[Path], faba_library: Path, append: bool = False
) -> None:
    """
    Obfuscate a sequence of MP3 files for a single Faba figure.

    Each MP3 file is copied to a temporary location, stripped of metadata,
    assigned a deterministic title, and converted to the proprietary MKI format.
    Resulting files are written into the corresponding figure folder inside
    the Faba library (e.g. ``K0104``).

    Parameters
    ----------
    figure_id:
        Four-digit Faba figure identifier (e.g. ``"0104"``).
    source_mp3_files:
        Ordered collection of source MP3 files to obfuscate for this figure.
    faba_library:
        Root path of the target Faba library (typically an ``MKI01`` folder).
    append:
        When True, MP3 files will be appended to an existing figure. New
        tracks are numbered after the highest existing ``.MKI`` file. When
        False (default) the figure will be created/overwritten starting at
        track 1.
    """
    if not source_mp3_files:
        logger.warning("No MP3 files provided for figure `%s`", figure_id)
        return

    logger.info("Converting files for figure: `%s`", figure_id)

    figure_path = faba_library / f"K{figure_id}"
    if append and not figure_path.exists():
        raise ValueError("You cannot append tracks to an unexisting figure")
    figure_path.mkdir(parents=True, exist_ok=True)

    existing_mki = sorted(p for p in figure_path.iterdir() if p.suffix.lower() == ".mki")
    start_index = (len(existing_mki) + 1) if append else 1

    for index, mp3_file in enumerate(sorted(source_mp3_files), start=start_index):
        logger.info(
            "Converting file %s [%d/%d]",
            mp3_file.name,
            index - start_index + 1,
            len(source_mp3_files),
        )

        file_number = f"{index:02d}"

        temp_handle = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        temp_mp3 = Path(temp_handle.name)
        temp_handle.close()  # Required for Windows compatibility

        try:
            shutil.copy(mp3_file, temp_mp3)

            new_title = f"K{figure_id}CP{file_number}"
            clear_tags_and_set_title(temp_mp3, new_title)

            obfuscated_file = figure_path / f"CP{file_number}.MKI"
            convert_mp3_to_mki(temp_mp3, obfuscated_file)
        finally:
            temp_mp3.unlink(missing_ok=True)


def obfuscate_mp3_library(
    faba_library_mp3: Path, faba_library: Path, default_figure_id: str = "0000"
) -> int:
    """
    Obfuscate a directory tree of MP3 files into a Faba-compatible MKI library.

    MP3 files are discovered recursively. If a file resides inside a directory
    named ``K####``, the digits are interpreted as the figure identifier.
    Otherwise, ``default_figure_id`` is used.

    Parameters
    ----------
    faba_library_mp3:
        Path containing source MP3 files. Subfolders named ``K####`` will be
        interpreted as per-figure groupings.
    faba_library:
        Destination Faba library root directory (typically an ``MKI01`` folder).
        Per-figure subfolders (e.g. ``K0104``) will be created as needed.
    default_figure_id:
        Figure identifier to use when no ``K####`` directory can be inferred.

    Returns
    -------
    int
        Total number of MP3 files processed.
    """
    # Monkeypatch to tolerate malformed ID3 headers

    all_mp3_files = sorted(p for p in faba_library_mp3.rglob("*") if p.suffix.lower() == ".mp3")
    files_by_figure: defaultdict[str, list[Path]] = defaultdict(list)

    for mp3_file in all_mp3_files:
        match = re.search(r"K(\d{4})$", mp3_file.parent.name)
        figure_id = match.group(1) if match else default_figure_id
        files_by_figure[figure_id].append(mp3_file)

    for figure_id, figure_mp3_files in files_by_figure.items():
        obfuscate_figure_mp3_files(figure_id, figure_mp3_files, faba_library)

    return len(all_mp3_files)


def deobfuscate_figure_mki_files(figure_id: str, faba_library: Path, output_folder: Path) -> int:
    """
    Deobfuscate all MKI files for a single Faba figure into MP3 files.

    MKI files are read from the corresponding figure directory inside the
    Faba library (e.g. ``K0104``) and converted back to standard MP3 files.
    The resulting MP3 files are written into a mirrored figure directory
    under the ``output_folder`` path.

    Parameters
    ----------
    figure_id:
        Four-digit Faba figure identifier (e.g. ``"0104"``).
    faba_library:
        Root path of the source Faba library (typically an ``MKI01`` folder).
    output_folder:
        Root path where deobfuscated MP3 files will be written.

    Returns
    -------
    int
        Number of MKI files converted for this figure.
    """
    figure_path = faba_library / f"K{figure_id}"
    if not figure_path.exists():
        logger.warning("Figure directory not found for figure `%s`", figure_id)
        return 0

    mki_files = sorted(p for p in figure_path.iterdir() if p.suffix.lower() == ".mki")

    if not mki_files:
        logger.warning("No MKI files found for figure `%s`", figure_id)
        return 0

    target_figure_path = output_folder / f"K{figure_id}"
    target_figure_path.mkdir(parents=True, exist_ok=True)

    for index, mki_file in enumerate(mki_files, start=1):
        target_file = (target_figure_path / mki_file.name).with_suffix(".mp3")
        logger.info("Converting file %s [%d/%d]", mki_file.name, index, len(mki_files))
        convert_mki_to_mp3(mki_file, target_file)

    return len(mki_files)


def deobfuscate_mki_library(faba_library: Path, faba_library_mp3: Path) -> int:
    """
    Deobfuscate a Faba MKI library back into standard MP3 files.

    MKI files are discovered recursively inside the Faba library. The original
    folder structure is preserved in the output directory, with file extensions
    converted to ``.mp3``.

    Parameters
    ----------
    faba_library:
        Source Faba library root directory (typically an ``MKI01`` folder)
        containing per-figure subdirectories with ``.MKI`` files.
    faba_library_mp3:
        Destination directory where deobfuscated MP3 files will be written.

    Returns
    -------
    int
        Total number of MKI files converted.
    """
    mki_files = sorted(p for p in faba_library.rglob("*") if p.suffix.lower() == ".mki")

    for index, mki_file in enumerate(mki_files, start=1):
        relative_path = mki_file.relative_to(faba_library)
        target_file = (faba_library_mp3 / relative_path).with_suffix(".mp3")
        target_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Converting file %s [%d/%d]", mki_file.name, index, len(mki_files))
        convert_mki_to_mp3(mki_file, target_file)

    return len(mki_files)
