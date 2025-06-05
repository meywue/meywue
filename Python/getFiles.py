import os
from pathlib import Path
from collections import defaultdict, Counter
import argparse

def get_files(directory, recursive=True):
    # directory = Path(directory)
    pattern = "**/*" if recursive else "*"
    return [f for f in directory.glob(pattern) if f.is_file()]

def summarize_files(files, allowed_exts=None):
    ext_counter = Counter()
    filtered_files = []

    for f in files:
        ext = f.suffix.lower().lstrip('.')  # Remove dot and lowercase
        ext_counter[ext] += 1
        if allowed_exts is None or ext in allowed_exts:
            filtered_files.append(f)

    return ext_counter, filtered_files

def print_summary(ext_counter, filtered_files, allowed_exts):
    print(f"\nFound {sum(ext_counter.values())} files:")
    for ext, count in sorted(ext_counter.items(), key=lambda x: -x[1]):
        print(f"{ext}: {count}")

    print(f"\nFiltered files: {len(filtered_files)} ({', '.join(allowed_exts)})")

def main():
    parser = argparse.ArgumentParser(
      description = "Get and summarize files in a directory."
    )
    parser.add_argument(
      "-D", "--dir",
      type = str,
      help = "Directory to search for files.",
      required = False
    )
    parser.add_argument(
      "-R", "--recursive",
      action = "store_true",
      help = "Search recursively in subdirectories.",
      default = False
    )

    args = parser.parse_args()

    directory = Path.cwd()
    if args.dir:
      directory = Path(args.dir)
      if not directory.is_dir():
        print(f"Error: {directory} is not a valid directory.")
        return

    print(f"Searching in directory: {directory}")

    allowed_exts = {"arw", "cr2", "jpg", "jpeg", "dng"}

    files = get_files(directory=directory, recursive=args.recursive)
    ext_counter, filtered_files = summarize_files(files, allowed_exts)
    print_summary(ext_counter, filtered_files, allowed_exts)

if __name__ == "__main__":
    main()
