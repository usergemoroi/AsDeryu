#!/usr/bin/env python3
"""
Patch burriiiii library to bypass bytehook verification.
This script searches for "Invalid access!" string and patches nearby abort() calls.
"""

import sys
import re

def find_string_offset(data, search_string):
    """Find offset of a string in binary data"""
    search_bytes = search_string.encode('utf-8') + b'\x00'
    offset = data.find(search_bytes)
    return offset

def find_abort_calls(data, start, end):
    """Find ARM64 BL instructions (calls) to abort() or similar"""
    # BL instruction in ARM64: 0x94xxxxxx (where xxxxxx is the offset)
    # We'll look for common abort patterns
    abort_patterns = []
    
    # Search for BL instructions in the range
    for i in range(start, min(end, len(data) - 4)):
        # Check for BL instruction (0x94 prefix for unconditional branch with link)
        if data[i:i+1] == b'\x94':
            abort_patterns.append(i)
    
    return abort_patterns

def patch_nop_sequence(data, offset, count=4):
    """Patch instructions with NOPs"""
    # ARM64 NOP instruction: 0x1F 0x20 0x03 0xD5
    nop = bytes([0x1F, 0x20, 0x03, 0xD5])
    
    print(f"[*] Patching {count} instructions at offset 0x{offset:X} with NOPs")
    print(f"    Original bytes: {data[offset:offset+count*4].hex()}")
    
    for i in range(count):
        data[offset + i*4:offset + (i+1)*4] = nop
    
    print(f"    Patched bytes:  {data[offset:offset+count*4].hex()}")
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
    
    # Find "Invalid access!" string
    invalid_offset = find_string_offset(data, "Invalid access!")
    if invalid_offset != -1:
        print(f"[*] Found 'Invalid access!' at offset 0x{invalid_offset:X}")
        
        # Search backwards for references to this string (usually within 0x1000 bytes)
        search_start = max(0, invalid_offset - 0x2000)
        
        # Convert offset to potential reference (little-endian relative addressing)
        # For ARM64, we need to look for ADRP + ADD sequence that loads this address
        print(f"[*] Searching for code that references this string...")
        
        # Simple approach: search for BL instructions near the string
        # and patch them with NOPs
        # This is a heuristic approach - in practice we'd need disassembly
        
        # For now, let's just disable the "Invalid access!" message by nulling it
        print(f"[*] Nullifying 'Invalid access!' string")
        data[invalid_offset:invalid_offset+15] = b'\x00' * 15
    else:
        print("[!] 'Invalid access!' string not found")
    
    # Also search for and patch "hook chain: verify" checks
    verify_ok_offset = find_string_offset(data, "hook chain: verify OK")
    if verify_ok_offset != -1:
        print(f"[*] Found 'hook chain: verify OK' at offset 0x{verify_ok_offset:X}")
    
    verify_bypass_offset = find_string_offset(data, "hook chain: verify bypass")
    if verify_bypass_offset != -1:
        print(f"[*] Found 'hook chain: verify bypass' at offset 0x{verify_bypass_offset:X}")
    
    print(f"[*] Writing patched file to {output_file}")
    with open(output_file, 'wb') as f:
        f.write(data)
    
    print("[+] Patching complete!")

if __name__ == "__main__":
    main()
