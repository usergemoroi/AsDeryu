#!/usr/bin/env python3
"""
Patch libclient.so to bypass anti-tampering checks.
This script patches the check() and licence() JNI functions to always return 1 (true).

ARM64 instructions:
    MOV X0, #1      => 20 00 80 D2
    RET             => C0 03 5F D6
"""

import sys
import struct

def patch_function(data, offset, name):
    """Patch a function to return 1 (true)"""
    # ARM64 instructions: MOV X0, #1; RET
    patch_bytes = bytes([0x20, 0x00, 0x80, 0xD2,  # MOV X0, #1
                        0xC0, 0x03, 0x5F, 0xD6])  # RET
    
    print(f"[*] Patching {name} at offset 0x{offset:X}")
    print(f"    Original bytes: {data[offset:offset+8].hex()}")
    
    # Apply patch
    data = data[:offset] + patch_bytes + data[offset+8:]
    
    print(f"    Patched bytes:  {data[offset:offset+8].hex()}")
    return data

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.so> <output.so>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print(f"[*] Reading {input_file}")
    with open(input_file, 'rb') as f:
        data = bytearray(f.read())
    
    print(f"[*] File size: {len(data)} bytes")
    
    # Patch Java_com_eternal_xdsdk_SuperJNI_00024Companion_licence at 0x161020
    data = patch_function(data, 0x161020, "SuperJNI.licence()")
    
    # Patch Java_com_eternal_xdsdk_SuperJNI_00024Companion_check at 0x1625bc
    data = patch_function(data, 0x1625bc, "SuperJNI.check()")
    
    print(f"[*] Writing patched file to {output_file}")
    with open(output_file, 'wb') as f:
        f.write(data)
    
    print("[+] Patching complete!")

if __name__ == "__main__":
    main()
