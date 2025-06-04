import os
import re
import subprocess

# Matches '20171206' in filenames like 'IMG-20171206-WA0008.jpg'
filename_date_regex = re.compile(r'(\d{4})(\d{2})(\d{2})')

def get_file_modify_time(filepath):
    try:
        result = subprocess.run(
            ["exiftool", "-s", "-s", "-s", "-FileModifyDate", filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        full_datetime = result.stdout.strip()

        parts = full_datetime.split()
        if len(parts) >= 2:
            date_str = parts[0]
            time_str = parts[1][:8]
            return date_str, time_str
    except subprocess.CalledProcessError as e:
        print(f"[ExifTool error] {e.stderr.strip()}")
        return None, None

def extract_exif_datetime(filename, filepath):
    match = filename_date_regex.search(filename)
    if not match:
        return None

    year, month, day = match.groups()
    filename_date_str = f"{year}:{month}:{day}"

    file_date_str, file_time_str = get_file_modify_time(filepath)
    if file_date_str == filename_date_str:
        return f"{filename_date_str} {file_time_str}"
    else:
        return f"{filename_date_str} 00:00:00"

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
        exif_date = extract_exif_datetime(filename, filepath)
        if exif_date:
            write_exif_date(filepath, exif_date)
            print(filename + "  " + exif_date)
        else:
            print(f"[Skip] Could not extract valid date from '{filename}'")

if __name__ == "__main__":
    process_directory(".")
