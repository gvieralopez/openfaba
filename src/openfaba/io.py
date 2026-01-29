import logging
import sys
from pathlib import Path

from openfaba.consts import BYTE_HIGH_NIBBLE, BYTE_LOW_NIBBLE_EVEN, BYTE_LOW_NIBBLE_ODD

from mutagen.id3 import ID3, TIT2
from mutagen.mp3 import MP3

logger = logging.getLogger(__name__)

def cipher_file(unencrypted_file: Path, encrypted_file: Path) -> None:
    """Apply custom byte transformation to an input file"""
    try:
        _cipher_file(unencrypted_file, encrypted_file)
        logger.info(f"Encryption complete. Output file: {encrypted_file}")
    except IOError as e:
        logger.error(f"Error processing {unencrypted_file}: {e}")
        sys.exit(1)



def clear_tags_and_set_title(mp3_file: Path, new_title: str) -> None:
    """Remove all MP3 tags and set a single title tag"""
    try:
        _clear_tags_and_set_title(mp3_file, new_title)
        logger.info(f"Title updated for {mp3_file}")
    except Exception as e:
        logger.error(f"Error processing {mp3_file}: {e}")
        sys.exit(1)

def decipher_file(encrypted_file: Path, unencrypted_file: Path) -> None:
    """ Reverse the cipher transformation to restore the original file """
    try:
        _decipher_file(encrypted_file, unencrypted_file)
        logger.info(f"Decryption complete. Output file: {unencrypted_file}")
    except IOError as e:
        logger.error(f"Error processing {encrypted_file}: {e}")
        sys.exit(1)
    

def _clear_tags_and_set_title(mp3_file: Path, new_title: str) -> None:
    tags = MP3(mp3_file, ID3=ID3)
    tags.delete()
    tags["TIT2"] = TIT2(encoding=3, text=new_title)
    tags.save()

def _decipher_file(encrypted_file: Path, unencrypted_file: Path) -> None:
    with encrypted_file.open("rb") as infile, unencrypted_file.open("wb") as outfile:
        for pos, byte in enumerate(infile.read()):
            byte_pos = pos % 4

            high_byte = byte  & 0xF0
            low_byte = byte  & 0x0F

            index_high = BYTE_HIGH_NIBBLE[byte_pos].index(high_byte)
            if low_byte in BYTE_LOW_NIBBLE_EVEN[byte_pos]:
                index_low = BYTE_LOW_NIBBLE_EVEN[byte_pos].index(low_byte)
            else:
                index_low = BYTE_LOW_NIBBLE_ODD[byte_pos].index(low_byte)
                index_high += 1
            
            outfile.write(bytes((index_low * 32 + index_high,)))

def _cipher_file(unencrypted_file: Path, encrypted_file: Path) -> None:
    with unencrypted_file.open("rb") as infile, encrypted_file.open("wb") as outfile:
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