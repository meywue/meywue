import os
import re
import subprocess

date_time = '2011:04:24 16:45:00'

def write_exif_date(filepath, exif_date):
    try:
        subprocess.run(
            ["exiftool", "-P", f"-DateTimeOriginal={exif_date}", "-overwrite_original", filepath],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"[OK] Wrote EXIF date '{exif_date}' to '{filepath}'")
    except subprocess.CalledProcessError as e:
        print(f"[Error] Failed to write EXIF to '{filepath}': {e.stderr.strip()}")

def process_directory(path="."):
    for filename in os.listdir(path):
        if not filename.lower().endswith((".jpg", ".jpeg", ".dng")):
            continue

        filepath = os.path.join(path, filename)
        write_exif_date(filepath, date_time)

if __name__ == "__main__":
    process_directory(".")