import codecs
import logging
import os
import re
import shutil
import sys
from pathlib import Path

import mutagen
from gooey import GooeyParser

from openfaba.io import cipher_file, decipher_file, clear_tags_and_set_title
from openfaba.utils import Unbuffered, id3header_constructor_monkeypatch

logger = logging.getLogger(__name__)


def encrypt_command(args):
    # monkeypatch out exceptions on invalid ID3 headers - we're only trying to delete
    # every ID3 tag after all...
    mutagen.id3._tags.ID3Header.__init__ = id3header_constructor_monkeypatch
    
    count = 0
    mp3_files = {}
    if args.extract_figure:
        for root, _, filenames in os.walk(args.source_folder):
            for filename in filenames:
                full_path = Path(root) / filename
                match = re.search(r'[\\/]K(\d{4})$', root)
                if filename.lower().endswith(".mp3") and match:
                    mp3_files.setdefault(match.group(1), []).append(full_path)
                    count += 1
        
    else:
        if not re.match(r"^\d{4}$", args.figure_id):
            logger.info("Error: Figure ID must be exactly 4 digits.")
            sys.exit(1)

        for root, _, filenames in os.walk(args.source_folder):
            for filename in filenames:
                full_path = Path(root) / filename
                if filename.lower().endswith(".mp3"):
                    mp3_files.setdefault(args.figure_id, []).append(full_path)
                    count += 1

    if count == 0:
        logger.info("No MP3 files found in the source folder.")
        sys.exit(1)

    iterator = 1
    for figure in mp3_files:
        figure_path = Path(args.target_folder) / f"K{figure}"
        figure_path.mkdir(exist_ok=True, parents=True)
        filenum = 1
        for file in sorted(mp3_files[figure]):
            logger.info(f"=========================[{iterator}/{count}]")
            logger.info(f"Processing {file}...")
            
            filenum_str = f"{filenum:02d}"
            new_title = f"K{figure}CP{filenum_str}"
            source_file = file
            target_file = figure_path / f"CP{filenum_str}"

            shutil.copy(source_file, target_file)
            clear_tags_and_set_title(target_file, new_title)

            encrypted_file = target_file.with_suffix(".MKI")
            cipher_file(target_file, encrypted_file)
            target_file.unlink()

            iterator += 1
            filenum += 1

    logger.info(f"Processing complete. Copy the files from '{args.target_folder}' directory to your Faba box.")

def dencrypt_command(args):
    count = 0
    mki_files = {}
    for root, _, filenames in os.walk(args.source_folder):
        for filename in filenames:
            rel_path = Path(root).relative_to(args.source_folder)
            if filename.lower().endswith(".mki"):
                mki_files.setdefault(str(rel_path), []).append(filename)
                count += 1

    if count == 0:
        logger.info("No MKI files found in the source folder.")
        sys.exit(1)

    iterator = 1
    for subdir in mki_files:
        subdir_path = Path(args.target_folder) / subdir
        subdir_path.mkdir(parents=True, exist_ok=True)
        for file in mki_files[subdir]:
            logger.info(f"=========================[{iterator}/{count}]")
            logger.info(f"Processing {Path(subdir) / file}...")
            source_file = Path(args.source_folder) / subdir / file
            target_file = Path(args.target_folder) / subdir / file

            if target_file.suffix.lower() == ".mki":
                target_file = target_file.with_suffix(".mp3")

            decipher_file(source_file, target_file)

            iterator += 1

    logger.info("Processing complete.")

def main():
    
    parser = GooeyParser(
        prog="Red Ele",
        description="Encrypt/Decrypt myfaba box MP3s",
    )
    
    subs = parser.add_subparsers(help="commands", dest="command")
    
    encrypt_group = subs.add_parser(
        "encrypt", prog="Encrypt",
    ).add_argument_group("")
    encrypt_group.add_argument(
        "-f",
        "--figure-id",
        metavar="Figure ID",
        help="Faba NFC chip identifier (4 digit number 0001-9999)",
        default="0000"
    )
    encrypt_group.add_argument(
        "-x",
        "--extract-figure",
        metavar="Extract Figure ID",
        action="store_true",
        help="Get figure ID from directory name (MP3 files have to be located in folder named K0001-K9999)",
    )
    encrypt_group.add_argument(
        "-s", 
        "--source-folder",
        metavar="Source Folder",
        help="Folder with MP3 files to process.",
        widget='DirChooser',
        gooey_options={'full_width':True}
    )
    encrypt_group.add_argument(
        "-t", 
        "--target-folder",
        metavar="Target Folder",
        help="Folder where generated FABA .MKI files will be stored. Subfolder for the figure will be created.",
        widget='DirChooser',
        gooey_options={'full_width':True}
    )
    
    decrypt_group = subs.add_parser(
        "decrypt", prog="Decrypt",
    ).add_argument_group("")
    decrypt_group.add_argument(
        "-s", 
        "--source-folder",
        metavar="Source Folder",
        help="Folder with MKI files to process. Supports recursion.",
        widget='DirChooser',
        gooey_options={'full_width':True}
    )
    decrypt_group.add_argument(
        "-t", 
        "--target-folder",
        metavar="Target Folder",
        help="Folder for decrypted MP3 files.",
        widget='DirChooser',
        gooey_options={'full_width':True}
    )
    

    args = parser.parse_args()
    
    if sys.stdout.encoding != 'UTF-8':
        sys.stdout = Unbuffered(codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict'))
    if sys.stderr.encoding != 'UTF-8':
        sys.stderr = Unbuffered(codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict'))    

    if not Path(args.source_folder).is_dir():
        logger.info(f"Error: Source folder '{args.source_folder}' does not exist or is not a directory.")
        sys.exit(1)

    if args.command=="encrypt":
        encrypt_command(args)
      
    
    if args.command=="decrypt":
        dencrypt_command(args)       
       


if __name__ == "__main__":
    if len(sys.argv) == 1:
        from gooey import Gooey
        main = Gooey(program_name='Red Ele',
                     default_size=(600, 600),
                     progress_regex=r"^=+\[(\d+)/(\d+)]$",
                     progress_expr="x[0] / x[1] * 100",
                     encoding='UTF-8',
                     navigation="TABBED",
                    )(main)
    # Gooey reruns the script with this parameter for the actual execution.
    # Since we don't use decorator to enable commandline use, remove this parameter
    # and just run the main when in commandline mode.
    if '--ignore-gooey' in sys.argv:
        sys.argv.remove('--ignore-gooey')
    main()
