#!/usr/bin/env python3
"""
Repack the patched APK files into a new unsigned APK.
"""

import os
import sys
import zipfile

def zip_directory(folder_path, output_path):
    """Create a ZIP file from a directory"""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                print(f"Adding: {arcname}")
                zipf.write(file_path, arcname)

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input_directory> <output.apk>")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_apk = sys.argv[2]
    
    print(f"[*] Repacking APK from {input_dir}")
    zip_directory(input_dir, output_apk)
    print(f"[+] APK repacked to {output_apk}")
    print(f"[*] File size: {os.path.getsize(output_apk)} bytes")

if __name__ == "__main__":
    main()
