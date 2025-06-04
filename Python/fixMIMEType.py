import os
import re
import subprocess

extensionsToMimetype = {
    'jpg': 'jpeg',
    'jpeg': 'jpeg',
    'png': 'png'
}

mimetypeToExtension = {
    'jpeg': 'jpg',
    'png': 'png'
}

def getMIMEType(filepath):
    try:
        result = subprocess.run(
            ["exiftool", "-FileType", "-MIMEType", "-s", "-s", "-s", filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        mimeType = result.stdout.split()[0].lower()
        return(mimeType)

    except subprocess.CalledProcessError as e:
        print(f"[ExifTool error] {e.stderr.strip()}")
        return None

def checkAndFixMIMEType(filepath):
    mimeType = getMIMEType(filepath)
    if not mimeType:
        return

    base, current_ext = os.path.splitext(filepath)
    current_ext = current_ext[1:].lower()
    if mimeType != extensionsToMimetype[current_ext]:
        oldpath = f"{base}.{current_ext}"
        newpath = f"{base}.{mimetypeToExtension[mimeType]}"
        print(f"mimetype vs extension mismatch found\n\told filepath: {oldpath}\n\tnew filepath: {oldpath}")
        os.rename(oldpath, newpath)

def process_directory(path="."):
    for filename in os.listdir(path):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        filepath = os.path.join(path, filename)
        checkAndFixMIMEType(filepath)

if __name__ == "__main__":
    process_directory(".")