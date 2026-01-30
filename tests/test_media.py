import logging
import tempfile
from pathlib import Path

from openfaba.media import deobfuscate_library, obfuscate_library

logger = logging.getLogger(__name__)


def test_obfuscate_deobfuscate_cycle(mki_library: Path) -> None:
    """Test that deobfuscating and obfuscating produces identical results."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Step 1: Deobfuscate the original library
        deobfuscate_dir = temp_path / "deobfuscated"
        deobfuscate_dir.mkdir()
        deobfuscate_library(mki_library, deobfuscate_dir)

        # Step 2: Obfuscate the deobfuscated files
        obfuscate_dir = temp_path / "obfuscated"
        obfuscate_dir.mkdir()
        obfuscate_library(deobfuscate_dir, obfuscate_dir)

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
