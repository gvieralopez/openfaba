import logging
import sys
from pathlib import Path

from mutagen.id3 import ID3, TIT2  # type:ignore [attr-defined]
from mutagen.mp3 import MP3

from openfaba.consts import BYTE_HIGH_NIBBLE, BYTE_LOW_NIBBLE_EVEN, BYTE_LOW_NIBBLE_ODD
from openfaba.utils import allow_invalid_synchsafe_in_mutagen

logger = logging.getLogger(__name__)


def clear_tags_and_set_title(mp3_file: Path, new_title: str) -> None:
    """Remove all MP3 tags and set a single title tag"""
    try:
        _clear_tags_and_set_title(mp3_file, new_title)
        logger.info(f"Title updated for {mp3_file}")
    except Exception as e:
        logger.error(f"Error processing {mp3_file}: {e}")
        sys.exit(1)


def convert_mp3_to_mki(mp3_file: Path, mki_file: Path) -> None:
    """Apply custom byte transformation to an mp3 file"""
    try:
        _convert_mp3_to_mki(mp3_file, mki_file)
        logger.info(f"Conversion complete. Output file: {mki_file}")
    except IOError as e:
        logger.error(f"Error processing {mp3_file}: {e}")
        sys.exit(1)


def convert_mki_to_mp3(mki_file: Path, mp3_file: Path) -> None:
    """Reverse the custom byte transformation to restore the original mp3 file"""
    try:
        _convert_mki_to_mp3(mki_file, mp3_file)
        logger.info(f"Conversion complete. Output file: {mp3_file}")
    except IOError as e:
        logger.error(f"Error processing {mki_file}: {e}")
        sys.exit(1)


def collect_all_mp3_files_in_folder(source: Path) -> list[Path]:
    return sorted(p for p in source.rglob("*.mp3") if p.is_file())


def _clear_tags_and_set_title(mp3_file: Path, new_title: str) -> None:
    with allow_invalid_synchsafe_in_mutagen():
        tags = MP3(mp3_file, ID3=ID3)
        # If title already matches, skip to preserve exact original bytes
        if "TIT2" in tags and len(tags) == 1 and str(tags["TIT2"].text[0]) == new_title:
            return

        # Ensure we write the title as UTF-16 (Encoding 1) and as a list of text
        tags.delete()
        tags["TIT2"] = TIT2(encoding=1, text=[new_title])
        tags.save(v2_version=3, padding=lambda x: 0)


def _convert_mp3_to_mki(mp3_file: Path, mki_file: Path) -> None:
    with mp3_file.open("rb") as infile, mki_file.open("wb") as outfile:
        for pos, byte in enumerate(infile.read()):
            byte_pos = pos % 4

            high_index = byte % 32
            low_index = byte // 32

            modified_byte = BYTE_HIGH_NIBBLE[byte_pos][high_index]

            if byte % 2 == 0:
                modified_byte += BYTE_LOW_NIBBLE_EVEN[byte_pos][low_index]
            else:
                modified_byte += BYTE_LOW_NIBBLE_ODD[byte_pos][low_index]

            outfile.write(bytes((modified_byte,)))


def _convert_mki_to_mp3(mki_file: Path, mp3_file: Path) -> None:
    with mki_file.open("rb") as infile, mp3_file.open("wb") as outfile:
        for pos, byte in enumerate(infile.read()):
            byte_pos = pos % 4

            high_byte = byte & 0xF0
            low_byte = byte & 0x0F

            index_high = BYTE_HIGH_NIBBLE[byte_pos].index(high_byte)
            if low_byte in BYTE_LOW_NIBBLE_EVEN[byte_pos]:
                index_low = BYTE_LOW_NIBBLE_EVEN[byte_pos].index(low_byte)
            else:
                index_low = BYTE_LOW_NIBBLE_ODD[byte_pos].index(low_byte)
                index_high += 1

            outfile.write(bytes((index_low * 32 + index_high,)))
