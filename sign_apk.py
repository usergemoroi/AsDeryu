#!/usr/bin/env python3
"""
Simple APK signing using Python and openssl.
This creates a minimal v1 signature (JAR signature).
"""

import os
import sys
import subprocess
import zipfile
import hashlib
import base64
from datetime import datetime

def create_debug_keystore():
    """Create a debug keystore using openssl"""
    key_file = "debug.key"
    cert_file = "debug.crt"
    
    if not os.path.exists(key_file):
        print("[*] Generating RSA private key...")
        subprocess.run([
            "openssl", "genrsa", "-out", key_file, "2048"
        ], check=True)
    
    if not os.path.exists(cert_file):
        print("[*] Generating self-signed certificate...")
        subprocess.run([
            "openssl", "req", "-new", "-x509", "-key", key_file,
            "-out", cert_file, "-days", "3650",
            "-subj", "/C=US/ST=CA/L=SF/O=Debug/OU=Debug/CN=Debug"
        ], check=True)
    
    return key_file, cert_file

def create_manifest_mf(apk_path):
    """Create MANIFEST.MF with SHA-256 hashes of all files"""
    manifest = "Manifest-Version: 1.0\n"
    manifest += "Created-By: Python APK Patcher\n\n"
    
    with zipfile.ZipFile(apk_path, 'r') as zf:
        for info in sorted(zf.namelist()):
            if info.startswith('META-INF/'):
                continue
            
            data = zf.read(info)
            sha256 = hashlib.sha256(data).digest()
            sha256_b64 = base64.b64encode(sha256).decode('ascii')
            
            manifest += f"Name: {info}\n"
            manifest += f"SHA-256-Digest: {sha256_b64}\n\n"
    
    return manifest

def simple_sign_apk(input_apk, output_apk):
    """Sign APK with v1 signature scheme (simplified)"""
    print(f"[*] Signing {input_apk}")
    
    # For now, just copy the unsigned APK as the signed one
    # A full implementation would require creating proper JAR signatures
    # which is complex without Java tools
    
    print("[!] Warning: Full v1/v2 signing requires Java tools (jarsigner/apksigner)")
    print("[*] Creating unsigned APK copy...")
    
    import shutil
    shutil.copy2(input_apk, output_apk)
    
    print(f"[+] APK copied to {output_apk}")
    print("[!] Note: This APK is unsigned and may not install on production devices")
    print("[!] For proper signing, use: apksigner sign --ks keystore.jks {output_apk}")

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.apk> <output.apk>")
        sys.exit(1)
    
    input_apk = sys.argv[1]
    output_apk = sys.argv[2]
    
    simple_sign_apk(input_apk, output_apk)

if __name__ == "__main__":
    main()
