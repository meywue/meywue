#!/usr/bin/env python3

import sys
import os
import re
import math
from pathlib import Path
from datetime import datetime

fileCount = 0
filesProcessed = 0
args = None

def checkFile(file):
    global fileCount, filesProcessed

    # This is only getting the ctime (time create) of the file not when it was taken.
    stctime = os.stat(file).st_ctime
    created_at = datetime.fromtimestamp(stctime)
    dir = "_processed/{}".format(created_at.date().__str__())
    filepath_new = "{}/{}".format(dir, file)

    try:
        os.mkdir(dir)
        print("Created directory '{}'.".format(dir))
    except Exception:
        # print("Directory '{}' already exist.".format(dir))
        pass

    try:
        os.rename(file, filepath_new)
    except Exception:
        print("Can't move file '{}'".format(file))

    filesProcessed += 1
    progress = filesProcessed / fileCount
    output = math.ceil(progress*10-0.5) * "*" + "  {0:.2f}%\b".format(progress * 100)
    print (output, end="\r")

def main():
    global fileCount

    path = "./"
    print("Working directory: {}".format(path))

    # recursive rglob
    # jpg = list(Path(path).rglob("*.[jJ][pP][gG]"))
    # arw = list(Path(path).rglob("*.[aA][rR][wW]"))
    # non-recursive glob
    jpg = list(Path(path).glob("*.[jJ][pP][gG]"))
    arw = list(Path(path).glob("*.[aA][rR][wW]"))
    fileCount = len(jpg) + len(arw)

    print("{} JPGs and {} ARWs have been found".format(len(jpg), len(arw)))

    print("Processing {} files...".format(fileCount))

    try:
        os.mkdir("_processed")
        print("Created directory ./_processed")
    except FileExistsError:
        print("Directory ./_processed already exist")

    for file in jpg:
        checkFile(file)

    for file in arw:
        checkFile(file)


    print("Done! Hit enter to quit the program!")
    while True:
        inp = input()   # Get the input
        if inp == "":       # If it is a blank line...
            break

if __name__ == "__main__":
    main()
