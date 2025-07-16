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
[ ] Pillow only works with JPG and PNG reliably. We need to use something like rawpy to compare RAW files.
[ ] Write resutls to a (json) file.
"""

import os
import sys
import hashlib
import argparse
import subprocess
import shutil
from collections import defaultdict
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime

args = None
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
        action='store_true',
        default=False,
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
        const="-1", # -1 means default output directory; we default to "_output" later, this is just for doing the check
        metavar="COPY_DIRECTORY",
        type=Path,
        help="Copy unique files to output dir (default: _output)\nWarning: If the output directory already exists, files will be copied into it, potentially overwriting existing files."
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

    print("args:", args)

    # --path
    if args.path is None:
        args.path = Path.cwd()
        print(f"[INFO] No --path given. Using current working directory: {args.path}")
        print()

    if not args.path.exists() or not args.path.is_dir():
        print(f"[ERROR] The path '{args.path}' is not a valid directory. Aborting.")
        sys.exit(1)
        print()
        return

    if args.verbose:
        print(f"[INFO] Searching in (unresolved): {args.path}")
    print(f"[INFO] Searching in: {args.path.resolve()}")

    # --recursive
    print(f"[INFO] Recursive search: {args.recursive}")
    print()

    if args.rename:
        if args.copy == None:
            print(f"[ERROR] --copy argument must be given when renaming files. Aborting.")
            sys.exit(1)
        args.rename = args.rename[0].strip()
        print(f"[INFO] Renaming files. Renaming expression: {args.rename}")

    # --copy
    if args.copy == Path("-1"):
        args.copy = args.path / "_output"
        print(f"[INFO] No --copy argument given. Using default output directory: '_output'")
    
    if args.copy:
        print(f"[INFO] Copying unique files to: {args.copy.resolve()}")
        if not args.copy.exists():
            print(f"[INFO] Creating output directory: {args.copy.resolve()}")
            args.copy.mkdir(parents=True, exist_ok=True)
        else:
            print(
                f"[INFO] Output directory already exists: {args.copy.resolve()}")
        print()

    # --delete
    if args.delete == "ask":
        if not confirm_deletion():
            print("[ERROR] Aborting.")
            sys.exit(1)
        else:
            print("[INFO] Proceeding with deletion...")
        print()
    elif args.delete == "Y":
        print("[INFO] Proceeding with deletion (no prompt)...")
        print()

    # --extensions
    args.extensions = ({ext.lower() for ext in args.extensions}
                       ) if args.extensions else default_extensions
    print(f"[INFO] File extensions: {', '.join(sorted(args.extensions))}")

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


def get_exif_tags(filepath: Path) -> dict:
    import subprocess
    import json
    try:
        result = subprocess.run(
            ["exiftool", "-j", str(filepath)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        data = json.loads(result.stdout)
        return data[0] if data else {}
    except Exception:
        return {}


def parse_exif_date(tags: dict) -> datetime | None:
    date_str = tags.get("DateTimeOriginal")
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return None


def get_value_score(tags: dict) -> int:
    """Score based on presence of valuable EXIF tags."""
    score_tags = [
        "FocalLength", "Aperture", "ShutterSpeed", "ISO", "CameraModelName", "LensModel"
    ]
    return sum(1 for tag in score_tags if tag in tags)


def determine_winner(paths: list[Path]) -> tuple[Path, list[Path]]:
    current_best = None
    losers = []

    for path in paths:
        tags = get_exif_tags(path)
        exif_date = parse_exif_date(tags)
        modify_time = path.stat().st_mtime
        score = get_value_score(tags)

        candidate = {
            "path": path,
            "date": exif_date,
            "mtime": modify_time,
            "score": score,
        }

        if current_best is None:
            current_best = candidate
            continue

        # --- Compare logic:
        better = False
        # 1) Has EXIF date, and earlier
        if candidate["date"] and not current_best["date"]:
            better = True
        elif candidate["date"] and current_best["date"]:
            better = candidate["date"] < current_best["date"]

        # 2) Fallback to file modification date
        elif not candidate["date"] and candidate["mtime"] < current_best["mtime"]:
            better = True

        # 3) Tiebreaker: more useful tags
        elif candidate["score"] > current_best["score"]:
            better = True

        if better:
            losers.append(current_best["path"])
            current_best = candidate
        else:
            losers.append(candidate["path"])

    return current_best["path"], losers


def delete_file(path: Path) -> None:
    """
    Deletes the file at the given path.
    Handles exceptions for file not found and permission errors.
    """
    try:
        path.unlink()
        print(f"[INFO] Deleted: {path}")
    except FileNotFoundError:
        print(f"[WARNING] Failed to delete {path}. File not found.")
    except PermissionError:
        print(f"[WARNING] Failed to delete {path}. Permission denied.")
    except Exception as e:
        print(f"[WARNING] Failed to delete {path}: {e}")

def find_duplicates(hash_map: defaultdict) -> None:
    print("\n=== find_duplicates ===")
    number_of_files = 0
    number_of_copied_files = 0
    for hash_value, paths in hash_map.items():
        number_of_files += len(paths)
        if len(paths) > 1:
            print(f"\n[INFO] Hash: {hash_value} ({len(paths)} entries)")
            winning_path, all_but_winner = determine_winner(paths)
            if args.verbose:
                print(f"[VERBOSE] Winner: {winning_path}")
                print("[VERBOSE] Loosers:")
                for path in all_but_winner:
                    print(f"\t- {path}")

            if args.copy:
                new_path = args.copy / winning_path.name
                print(f"[INFO] Copying winner to: {args.copy.resolve()}")
                try:
                    shutil.copy2(winning_path, new_path)
                    print(f"[INFO] Copied {winning_path} to {new_path}")
                    number_of_copied_files += 1

                    if args.delete:
                        delete_file(winning_path)

                except FileNotFoundError:
                    print(f"[WARNING] Failed to copy {winning_path}. File not found.")
                except Exception as e:
                    print(f"[WARNING] Failed to copy {winning_path}: {e}")

            if args.delete:
                for path in all_but_winner:
                    delete_file(path)


        elif len(paths) == 1:
            if args.copy:
                new_path = args.copy / paths[0].name
                print(f"\n[INFO] Copying single file to: {args.copy.resolve()})")
                try:
                    shutil.copy2(paths[0], new_path)
                    print(f"[INFO] Copied {paths[0]} to {new_path}")
                    number_of_copied_files += 1

                    if args.delete:
                        delete_file(paths[0])
                        
                except FileNotFoundError:
                    print(f"[WARNING] Failed to copy {paths[0]}. File not found.")
                except Exception as e:
                    print(f"[WARNING] Failed to copy {paths[0]}: {e}")

    print(f"\n[INFO] Found {len(hash_map)} unique hashes in {number_of_files} files.")
    if number_of_copied_files > 0:
        print(f"[INFO] Copied {number_of_copied_files} unique files to {args.copy.resolve()}")

    print()


def main() -> None:
    global args
    args = parse_args()

    hash_map = get_file_hashmap(args.path, recursive=args.recursive, extensions=args.extensions)
    find_duplicates(hash_map)


if __name__ == "__main__":
    main()
