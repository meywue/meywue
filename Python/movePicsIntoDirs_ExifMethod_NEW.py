#!/usr/bin/env python3

# Dependencies:
# exifread
#   `python -m pip install --upgrade pip`
#   `python -m pip install --upgrade exifread`

# install https://exiftool.org/

import sys
import os
import re
import math
from pathlib import Path
from datetime import datetime
import exifread
import subprocess
import json
# from memory_profiler import profile

xmps = {}
fileCount = 0
filesProcessed = 0
args = None

exif_key_short = "DateTimeOriginal"
exif_key = "EXIF " + exif_key_short
regex_pattern = re.compile(r'(\d+):(\d+):(\d+)')

filename_regex = re.compile(r'(\w+)')

def get_exif_date(filepath):
    try:
        result = subprocess.run(
            ["exiftool", "-j", "-DateTimeOriginal", filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        metadata = json.loads(result.stdout)
        if metadata and "DateTimeOriginal" in metadata[0]:
            return metadata[0]["DateTimeOriginal"]
    except subprocess.CalledProcessError as e:
        print(f"[ExifTool error] {e.stderr.strip()}")
    return None

def checkFile(file):
    global fileCount, filesProcessed, xmps

    exif_value_as_string = get_exif_date(file)
    if exif_value_as_string:
        matches = regex_pattern.match(exif_value_as_string)
        if not matches:
            print(f"Failed to parse EXIF date: '{exif_value_as_string}' in file '{file}'")
            return

        year, month, day = matches.group(1), matches.group(2), matches.group(3)
        dir = f"_processed/{year}-{month}-{day}"
        filepath_new = f"{dir}/{file}"
        print("filepath_new:", filepath_new)

        try:
            os.makedirs(dir, exist_ok=True)
        except Exception as e:
            print(f"Couldn't create directory '{dir}': {e}")
            return

        try:
            os.rename(file, filepath_new)
            reg_group = filename_regex.match(str(file)).group(1)
            if reg_group in xmps:
                xmp_old_filename = xmps[reg_group]
                xmp_new_filename = f"{dir}/{xmp_old_filename}"
                os.rename(xmp_old_filename, xmp_new_filename)
        except Exception as exception:
            print(f"Can't move file '{file}': {repr(exception)}")
    else:
        print(f"[Skip] No 'DateTimeOriginal' EXIF tag found for '{file}'.")

    filesProcessed += 1
    progress = filesProcessed / fileCount
    output = math.ceil(progress * 10 - 0.5) * "*" + f"  {progress * 100:.2f}%"
    print(output, end="\r")

# @profile
def main():
    global fileCount, xmps

    path = "./"
    print("Working directory: {}".format(path))

    # recursive rglob
    # jpg = list(Path(path).rglob("*.[jJ][pP][gG]"))
    # arw = list(Path(path).rglob("*.[aA][rR][wW]"))
    # non-recursive glob
    jpg = list(Path(path).glob("*.[jJ][pP][gG]"))
    # jpg = list(Path(path).glob("*.[jJ][pP][eE][gG]"))
    # jpg = list(Path(path).glob("*.[pP][nN][gG]"))
    # arw = list(Path(path).glob("*.[aA][rR][wW]"))
    # arw = list(Path(path).glob("*.[cC][rR][2]"))
    # arw = list(Path(path).glob("*.[oO][rR][fF]"))
    arw = list(Path(path).glob("*.[dD][nN][gG]"))
    xmp = list(Path(path).glob("*.[xX][mM][pP]"))

    for file in xmp:
        matches = filename_regex.match(str(file))
        xmps[matches.group(1)] = file

    # print("xmps")
    # print(xmps)

    print("xmp")
    print(xmp)
    print(type(xmp))
    fileCount = len(jpg) + len(arw)

    print("{} JPGs and {} ARWs have been found".format(len(jpg), len(arw)))

    print("Processing {} files...".format(fileCount))

    try:
        os.mkdir("_processed")
        print("Created directory ./_processed")
    except FileExistsError:
        # print("Directory ./_processed already exist")
        pass

    for file in jpg:
        checkFile(file)

    for file in arw:
        checkFile(file)

    print("\n\nDone! Hit enter to quit the program!")
    while True:
        inp = input()   # Get the input
        if inp == "":       # If it is a blank line...
            break

if __name__ == "__main__":
    main()
