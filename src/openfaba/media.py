import logging
import re
import shutil
import tempfile
from collections import defaultdict
from pathlib import Path

import mutagen

from openfaba.io import clear_tags_and_set_title, convert_mki_to_mp3, convert_mp3_to_mki
from openfaba.utils import id3header_constructor_monkeypatch

logger = logging.getLogger(__name__)


def obfuscate_figure_files(figure_id: str, mp3_files: list[Path], target_folder: Path) -> None:
    """Encrypt MP3 files for a specific figure."""
    if not mp3_files:
        logger.warning(f"No MP3 files provided for figure `{figure_id}`")
        return
    logger.info(f"Converting files for figure: `{figure_id}`")

    figure_path = target_folder / f"K{figure_id}"
    figure_path.mkdir(parents=True, exist_ok=True)

    for i, mp3_file in enumerate(sorted(mp3_files), start=1):
        logger.info(f"Converting file {mp3_file.name} [{i}/{len(mp3_files)}]")

        filenum_str = f"{i:02d}"

        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        temp_mp3 = Path(tmp.name)
        tmp.close()  # Close so we can write to it on Windows

        try:
            shutil.copy(mp3_file, temp_mp3)

            new_title = f"K{figure_id}CP{filenum_str}"
            clear_tags_and_set_title(temp_mp3, new_title)

            obfuscated_file = figure_path / f"CP{filenum_str}.MKI"
            convert_mp3_to_mki(temp_mp3, obfuscated_file)
        finally:
            temp_mp3.unlink(missing_ok=True)


def obfuscate_library(source_folder: Path, target_folder: Path) -> int:
    """Obfuscate MP3 files for Faba box."""
    # monkeypatch out exceptions on invalid ID3 headers
    mutagen.id3._tags.ID3Header.__init__ = id3header_constructor_monkeypatch

    all_mp3_files = sorted([p for p in source_folder.rglob("*") if p.suffix.lower() == ".mp3"])
    files_by_figure: defaultdict[str, list[Path]] = defaultdict(list)

    for mp3 in all_mp3_files:
        # Expect parent directory like ".../K####"
        match = re.search(r"K(\d{4})$", mp3.parent.name)
        figure_id = match.group(1) if match else "0000"
        files_by_figure[figure_id].append(mp3)

    for figure_id, mp3_files in files_by_figure.items():
        obfuscate_figure_files(figure_id, mp3_files, target_folder)

    return len(all_mp3_files)


def deobfuscate_library(source_folder: Path, target_folder: Path) -> int:
    """Deobfuscate MKI files from Faba box."""
    mki_files = sorted([p for p in source_folder.rglob("*") if p.suffix.lower() == ".mki"])

    for i, mki_file in enumerate(mki_files, start=1):
        rel_path = mki_file.relative_to(source_folder)
        target_file = target_folder / rel_path
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file = target_file.with_suffix(".mp3")

        logger.info(f"Converting file {mki_file.name} [{i}/{len(mki_files)}]")
        convert_mki_to_mp3(mki_file, target_file)

    return len(mki_files)
