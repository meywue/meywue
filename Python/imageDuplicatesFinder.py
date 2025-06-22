"""
Description:
Find duplicate images in a directory based on file content hash.
This script uses the SHA256 hash of the file contents to identify duplicates.

Requirements:
* Python 3.6 or higher
* Pillow library for image processing (`pip install pillow`)

ToDo:
[ ] Implement detailed comparison of EXIF dates for duplicates.
[ ] Handle duplicates.
[ ] get_image_hash compares the raw image content; A JPG and PNG with the same image yield the same hash.
[ ] Pillow only works with JPG and PNG reliably. We need to use something like rawpy to compare RAW files.
"""

import os
import sys
import hashlib
import argparse
from collections import defaultdict
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS


def parse_args():
    """
    Parses command line arguments for the script.
    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description='Find duplicate images in a directory'
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Verbose output"
    )
    parser.add_argument(
        '--path',
        type=Path,
        help='Path to the directory to search for duplicates'
    )
    parser.add_argument(
        '--recursive',
        action='store_true',
        help='Search recursively in subdirectories'
    )

    parser.add_argument(
        "--copy",
        nargs="?",
        const="_output",
        metavar="copy_directory",
        type=Path,
        help="Copy unique files to output dir (default: _output)"
    )
    parser.add_argument(
        '--delete', 
        nargs="?", 
        const="ask",
        choices=["ask", "Y"],
        help='Delete unnecessary duplicate files'
    )

    args = parser.parse_args()


    # --path
    if args.path is None:
        args.path = Path.cwd()
        print(
            f"🔵 No --path given. Using current working directory: {args.path}"
        )

    if not args.path.exists() or not args.path.is_dir():
        print(f"🔴 The path '{args.path}' is not a valid directory.")
        return

    if args.verbose:
        print(f"🔎 Searching in (unresolved): {args.path}")
    print(f"🔎 Searching in: {args.path.resolve()}")

    # --recursive
    print(f"🔁 Recursive search: {args.recursive}")

    # --copy
    if args.copy:
        print(f"📂 Copying unique files to: {args.copy.resolve()}")

    # --delete
    if args.delete == "ask":
        if not confirm_deletion():
            print("🔴 Aborting.")
            sys.exit(1)
        else:
            print("🗑️ Proceeding with deletion...")
    elif args.delete == "Y":
        print("🗑️ Proceeding with deletion (no prompt)...")

    return args


def confirm_deletion():
    try:
        choice = input("⚠️  Are you sure you want to delete duplicate files? This step is irreversible. (y/N): ").strip().lower()
        return choice == "y"
    except KeyboardInterrupt:
        print("\n❌ Cancelled.")
        return False


def get_image_hash(filepath: Path) -> str:
    """
    Creates the SHA256 hash of image content using hashlib and return it.

    Uses Pillow to read the image and convert it to bytes.
    This function normalizes the image format to RGB to ensure consistent hashing.

    A JPG and PNG of the same image will be considered duplicates.

    Args:
        filepath (Path): The path to the file.

    Returns:
        str: The SHA256 hash of the image content.
    """
    with Image.open(filepath) as img:
        img = img.convert("RGB")  # Normalize format
        data = img.tobytes()
        return hashlib.sha256(data).hexdigest()


def get_file_hash(filepath: Path) -> str:
    """
    Creates the SHA256 hash of the file using hashlib and return it.

    Args:
        filepath (Path): The path to the file.

    Returns:
        str: The SHA256 hash of the file.
    """
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()


def get_exif_datetime(filepath):
    """
    Returns the EXIF 'DateTimeOriginal' if available.
    If the EXIF data is not available, returns None.

    Args:
        filepath (Path): The path to the file.

    Returns:
        str: EXIF data of the file.
    """
    try:
        image = Image.open(filepath)
        exif_data = image._getexif()
        if not exif_data:
            return None
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == 'DateTimeOriginal':
                return value
    except Exception:
        return None


def get_hashmap(directory: Path,
                    recursive=True,
                    extensions={'jpg', 'jpeg', 'png', 'cr2', 'arw', 'dng'}):
    """
    Returns a hashmap with all found files where the key is a SHA256 hash and the value is the file path.

    Args:
        directory (Path): The path to the directory where the search is started.
        recursive (bool): Recursive search.
        extensions (set): File extensions being used when searching for files.

    Returns:
        defaultdict: Hashmap of the files found.
    """
    hash_map = defaultdict(list)

    pattern = "**/*" if recursive else "*"
    files = [
        f for f in directory.glob(pattern)
        if f.is_file() and f.suffix[1:].lower() in extensions
    ]

    for file in files:
        try:
            hash_value = get_image_hash(file)
            # hash_value = get_file_hash(file)
            hash_map[hash_value].append(file)

        except Exception as e:
            print(f"Error processing {file}: {e}")

    return hash_map

    
def find_duplicates(hash_map: defaultdict):
    print("\n=== Duplicate Images ===")
    for hash_value, paths in hash_map.items():
        if len(paths) > 1:
            print(f"\nHash: {hash_value} ({len(paths)} entries)")
            for path in paths:
                print(f"  - {path}")

    print()


def main():
    args = parse_args()

    hash_map = get_hashmap(args.path, recursive=args.recursive, extensions={'jpg', 'jpeg', 'png'})
    find_duplicates(hash_map)


if __name__ == "__main__":
    main()
