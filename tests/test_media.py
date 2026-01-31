import logging
import tempfile
from pathlib import Path

import pytest

from openfaba.media import (
    deobfuscate_figure_mki_files,
    deobfuscate_mki_library,
    obfuscate_figure_mp3_files,
    obfuscate_mp3_library,
)

logger = logging.getLogger(__name__)


def test_obfuscate_deobfuscate_cycle(mki_library: Path) -> None:
    """Test that deobfuscating and obfuscating produces identical results."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Step 1: Deobfuscate the original library
        deobfuscate_dir = temp_path / "deobfuscated"
        deobfuscate_dir.mkdir()
        deobfuscate_mki_library(mki_library, deobfuscate_dir)

        # Step 2: Obfuscate the deobfuscated files
        obfuscate_dir = temp_path / "obfuscated"
        obfuscate_dir.mkdir()
        obfuscate_mp3_library(deobfuscate_dir, obfuscate_dir)

        # Step 3: Compare the original and newly obfuscated files
        # Get all files from the original library
        original_files = sorted(mki_library.rglob("*"))
        original_files = [f for f in original_files if f.is_file()]

        # Get all files from the re-obfuscated library
        new_files = sorted(obfuscate_dir.rglob("*"))
        new_files = [f for f in new_files if f.is_file()]

        # Check that we have the same number of files
        assert len(original_files) == len(new_files), (
            f"Number of files mismatch: {len(original_files)} original vs {len(new_files)} new"
        )

        # Compare each file
        for original_file, new_file in zip(original_files, new_files, strict=True):
            # Check file names match relative to their parent figure folder
            original_rel = original_file.relative_to(mki_library)
            new_rel = new_file.relative_to(obfuscate_dir)

            assert original_rel == new_rel, f"File path mismatch: {original_rel} vs {new_rel}"

            # Compare file contents
            with original_file.open("rb") as f1, new_file.open("rb") as f2:
                original_content = f1.read()
                new_content = f2.read()

                assert original_content == new_content, f"File content mismatch for {original_rel}"

        logger.info(f"Successfully verified {len(original_files)} files in cycle test")


def test_insert_and_extend_cycle(mki_library: Path) -> None:
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)

        # Deobfuscate a small figure from the fixture to obtain valid MP3 files
        deob_dir = td_path / "deob"
        deob_dir.mkdir()
        converted = deobfuscate_figure_mki_files("3001", mki_library, deob_dir)
        assert converted > 0

        source_mp3 = sorted(p for p in (deob_dir / "K3001").rglob("*.mp3"))
        assert source_mp3, "deobfuscation did not produce mp3 files"

        # Create a fresh FABA library and insert the figure
        faba_lib = td_path / "faba"
        faba_lib.mkdir()

        obfuscate_figure_mp3_files("3001", source_mp3, faba_lib, append=False)
        kpath = faba_lib / "K3001"
        mkis = sorted(p for p in kpath.iterdir() if p.suffix.lower() == ".mki")
        assert len(mkis) == len(source_mp3)

        # Append the same files again
        obfuscate_figure_mp3_files("3001", source_mp3, faba_lib, append=True)
        mkis2 = sorted(p for p in kpath.iterdir() if p.suffix.lower() == ".mki")
        assert len(mkis2) == len(source_mp3) * 2

        # Appending to a non-existing figure should raise
        with pytest.raises(ValueError):
            obfuscate_figure_mp3_files("9999", source_mp3, faba_lib, append=True)
