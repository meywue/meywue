#!/usr/bin/env python3

# Dependencies:
# exifread
#   `python -m pip install --upgrade pip`
#   `python -m pip install --upgrade exifread`

import sys
import os
import re
import math
from pathlib import Path
from datetime import datetime
import exifread
# from memory_profiler import profile

xmps = {}
fileCount = 0
filesProcessed = 0
args = None

exif_key_short = "DateTimeOriginal"
exif_key = "EXIF " + exif_key_short
regex_pattern = re.compile(r'(\d+):(\d+):(\d+)')

filename_regex = re.compile(r'(\w+)')

# @profile
def checkFile(file):
    global fileCount, filesProcessed, xmps

    # Open image file for reading (must be in binary mode)
    f = open(file, 'rb')

    # Return Exif tags
    # Don’t process makernote tags, don’t extract the thumbnail image (if any).
    # No need to read any further than 'DateTimeOrigial'
    tags = exifread.process_file(f, details=False, stop_tag=exif_key_short)
    # for tag in tags.keys():
    #     if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
    #         print("Key: %s, value %s" % (tag, tags[tag]))
    f.close()

    if exif_key in tags.keys():
        exif_value_as_string = str(tags[exif_key])
        # print("key: ", exif_key, "value: ", exif_value_as_string)
        matches = regex_pattern.match(exif_value_as_string)
        # print("matches: ", matches.groups())
        year = matches.group(1)
        month = matches.group(2)
        day = matches.group(3)

        dir = f"_processed/{year}-{month}-{day}"
        filepath_new = f"{dir}/{file}"
        print("filepath_new: ", filepath_new)

        try:
            os.mkdir(dir)
            print("Created directory '{}'.".format(dir))
        except Exception:
            # print("Directory '{}' already exist.".format(dir))
            pass

        try:
            os.rename(file, filepath_new)
            reg_group = filename_regex.match(str(file)).group(1)
            if reg_group in xmps:
                xmp_old_filename = xmps[reg_group]
                xpm_new_filename = f"{dir}/{xmp_old_filename}"
                os.rename(xmp_old_filename, xpm_new_filename)
            # pass
        except Exception as exception:
            print(f"Can't move file '{file}' : {repr(exception)}")
    else:
        print(f"Exif data for file '{file}' has no entry for '{exif_key}'. Skipping file!")

    filesProcessed += 1
    progress = filesProcessed / fileCount
    output = math.ceil(progress*10-0.5) * "*" + "  {0:.2f}%\b".format(progress * 100)
    print (output, end="\r")

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
