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
"""

import hashlib
from pathlib import Path
from collections import defaultdict
from PIL import Image
from PIL.ExifTags import TAGS
import os
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description='Find duplicate images in a directory')
    parser.add_argument('--path',
                        type=Path,
                        help='Path to the directory to search for duplicates')
    parser.add_argument('--recursive',
                        action='store_true',
                        help='Search recursively in subdirectories')

    args = parser.parse_args()

    if args.path is None:
        args.path = Path.cwd()
        print(
            f"[INFO] No --path given. Using current working directory: {args.path}"
        )

    return args


def get_image_hash(filepath):
    """Return SHA256 hash of file contents."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()


def get_exif_datetime(filepath):
    """Return EXIF 'DateTimeOriginal' if available."""
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


def find_duplicates(directory,
                    recursive=True,
                    extensions={'jpg', 'jpeg', 'png', 'cr2', 'arw', 'dng'}):
    hash_map = defaultdict(list)
    mismatched_dates = []

    pattern = "**/*" if recursive else "*"
    files = [
        f for f in Path(directory).glob(pattern)
        if f.is_file() and f.suffix[1:].lower() in extensions
    ]

    for file in files:
        try:
            hash_value = get_image_hash(file)
            hash_map[hash_value].append(file)

            exif_date = get_exif_datetime(file)
            mod_time = os.path.getmtime(file)
            mod_date = str(Path(file).stat().st_mtime)

            if exif_date:
                # optionally compare formatted dates
                pass  # Implement detailed comparison here
        except Exception as e:
            print(f"Error processing {file}: {e}")

    print("\n=== Duplicate Images ===")
    for hash_value, paths in hash_map.items():
        if len(paths) > 1:
            print(f"\nHash: {hash_value}")
            for path in paths:
                print(f"  - {path}")

    print()


def main():
    args = parse_args()

    if not args.path.exists() or not args.path.is_dir():
        print(f"[ERROR] The path '{args.path}' is not a valid directory.")
        return

    print(f"Searching in (unresolved): {args.path}")
    print(f"Searching in: {args.path.resolve()}")
    print(f"Recursive: {args.recursive}")

    find_duplicates(args.path, recursive=args.recursive)


if __name__ == "__main__":
    main()
