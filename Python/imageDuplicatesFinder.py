"""
Description:
Find duplicate images in a directory based on file content hash.
This script uses the SHA256 hash of the file contents to identify duplicates.

Requirements:
* Python 3.6 or higher
* Pillow library for image processing (`pip install pillow`)
* exiftools

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
import subprocess
from collections import defaultdict
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS


default_extensions = {'jpg', 'png'}


def parse_args():
    """
    Parses command line arguments for the script.
    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="""
Find duplicate images in a directory based on file content hash.

This script uses the SHA256 hash of the file contents to identify duplicates.

Requirements:
  • Python 3.6 or higher
  • Pillow library (`pip install pillow`)
  • exiftool (must be in PATH)
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
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
        metavar="COPY_DIRECTORY",
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
    parser.add_argument(
        "-ext", "--extensions",
        nargs="+",
        metavar="EXTENSIONS",
        help=f"Define file extensions to search for (default: {default_extensions})"
    )
    parser.add_argument(
        "--rename",
        nargs=1,
        metavar="RENAME_EXPRESSION",
        help="TODO: Rename files using a custom expression. "
             "Use {hash} for the file hash, {datetime} for the EXIF DateTimeOriginal, "
             "and {filename} for the original filename."
    )
    args = parser.parse_args()

    # --path
    if args.path is None:
        args.path = Path.cwd()
        print(
            f"[INFO] No --path given. Using current working directory: {args.path}"
        )

    if not args.path.exists() or not args.path.is_dir():
        print(f"[ERROR] The path '{args.path}' is not a valid directory.")
        return

    if args.verbose:
        print(f"Searching in (unresolved): {args.path}")
    print(f"Searching in: {args.path.resolve()}")

    # --recursive
    print(f"Recursive search: {args.recursive}")

    # --copy
    if args.copy:
        print(f"Copying unique files to: {args.copy.resolve()}")
        if not args.copy.exists():
            print(f"[INFO] Creating output directory: {args.copy.resolve()}")
            args.copy.mkdir(parents=True, exist_ok=True)
        else:
            print(
                f"[INFO] Output directory already exists: {args.copy.resolve()}")
    else:
        if args.rename:
            print("[ERROR] --copy is required when using --rename.")
            sys.exit(1)

    if args.rename:
        args.rename = args.rename[0].strip()
        print(f"Renaming files. Renaming expression: {args.rename}")

    # --delete
    if args.delete == "ask":
        if not confirm_deletion():
            print("[ERROR] Aborting.")
            sys.exit(1)
        else:
            print("Proceeding with deletion...")
    elif args.delete == "Y":
        print("Proceeding with deletion (no prompt)...")

    # --extensions
    args.extensions = ({ext.lower() for ext in args.extensions}
                       ) if args.extensions else default_extensions
    print(f"File extensions: {', '.join(sorted(args.extensions))}")

    return args


def confirm_deletion():
    try:
        choice = input(
            "[WARN] Are you sure you want to delete duplicate files? This step is irreversible. (y/N): ").strip().lower()
        return choice == "y"
    except KeyboardInterrupt:
        print("\nCancelled.")
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


def get_exif_datetime(filepath) -> str:
    """
    Returns the EXIF 'DateTimeOriginal' if available.
    If the EXIF data is not available, returns None.

    Args:
        filepath (Path): The path to the file.

    Returns:
        str: EXIF data of the file.
    """
    try:
        result = subprocess.run(
            ["exiftool", "-s", "-s", "-s", "-DateTimeOriginal", str(filepath)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        output = result.stdout.strip()
        return output if output else None
    except subprocess.CalledProcessError:
        return None


def get_file_hashmap(directory: Path,
                     recursive=True,
                     extensions={'jpg', 'jpeg', 'png', 'cr2', 'arw', 'dng'}) -> defaultdict:
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


def find_duplicates(hash_map: defaultdict) -> None:
    print("\n=== Duplicate Images ===")
    for hash_value, paths in hash_map.items():
        if len(paths) > 1:
            print(f"\nHash: {hash_value} ({len(paths)} entries)")
            winning_path, all_but_winner = determine_winner(paths)
            # print(f"Winner: {winning_path}")
            for path in paths:
                print(f"  - {path}")

    print()


def determine_winner(paths: list) -> tuple[Path, list[Path]]:
    """
    Determines the winner file from a list of files.
    The winner is the file with the earliest EXIF date or the first file if no EXIF date is available.

    Args:
        paths (list): List of file paths.

    Returns:
        The Path of the winner file.
    """
    all_but_winner = []
    current_winner = None
    for k, path in enumerate(paths):
        if k == 0:
            current_winner = {
                'path': path,
                'date_time': get_exif_datetime(path)
            }
            print(current_winner)
            continue

    return current_winner['path'], all_but_winner


def main() -> None:
    args = parse_args()

    hash_map = get_file_hashmap(
        args.path, recursive=args.recursive, extensions=args.extensions)
    find_duplicates(hash_map)


if __name__ == "__main__":
    main()
