# Patch Summary - Android APK Anti-Tampering Bypass

## Date: 2026-02-10

## Objective
Disable anti-tampering protection in Android APK to allow installation after re-signing with a different certificate.

## Files Modified

### 1. lib/arm64-v8a/libclient.so

**Function 1: SuperJNI.licence()**
- **Symbol:** `Java_com_eternal_xdsdk_SuperJNI_00024Companion_licence`
- **Offset:** 0x161020
- **Original bytes:** `ff 83 03 d1 fd 7b 08 a9`
- **Patched bytes:** `20 00 80 d2 c0 03 5f d6`
- **Disassembly:**
  ```assembly
  MOV X0, #1    ; Return value = 1 (true)
  RET           ; Return immediately
  ```

**Function 2: SuperJNI.check()**
- **Symbol:** `Java_com_eternal_xdsdk_SuperJNI_00024Companion_check`
- **Offset:** 0x1625BC
- **Original bytes:** `fd 7b ba a9 fc 6f 01 a9`
- **Patched bytes:** `20 00 80 d2 c0 03 5f d6`
- **Disassembly:**
  ```assembly
  MOV X0, #1    ; Return value = 1 (true)
  RET           ; Return immediately
  ```

### 2. assets/burriiiii/arm64/lib2f8c0b3257fcc345.so

**Bytehook Protection Bypass**
- **Offset:** 0xC52A
- **Original:** "Invalid access!" error string
- **Patched:** Nullified (replaced with zeros)
- **Effect:** Prevents bytehook framework from triggering abort() on signature mismatch

## Verification

### Command to verify patches:
```bash
# Check licence function
unzip -p base-patched-unsigned.apk lib/arm64-v8a/libclient.so | \
  dd bs=1 skip=$((0x161020)) count=8 2>/dev/null | od -An -tx1
# Expected: 20 00 80 d2 c0 03 5f d6

# Check check function
unzip -p base-patched-unsigned.apk lib/arm64-v8a/libclient.so | \
  dd bs=1 skip=$((0x1625bc)) count=8 2>/dev/null | od -An -tx1
# Expected: 20 00 80 d2 c0 03 5f d6
```

### Results: ✅ VERIFIED
- Both functions correctly patched with `MOV X0, #1; RET` instructions
- Bytehook "Invalid access!" string nullified
- APK repackaged successfully (5.3 MB unsigned)

## Output Files

1. **base.apk** - Original unmodified APK (6.2 MB)
2. **base-patched-unsigned.apk** - Patched APK ready for signing (5.3 MB)
3. **patch_lib.py** - Python script for patching libclient.so
4. **patch_burriiiii.py** - Python script for patching bytehook protection
5. **repack_apk.py** - Python script to repack APK
6. **README.md** - Full documentation and signing instructions

## Next Steps

The patched APK must be signed before installation:

```bash
# Using apksigner
apksigner sign --ks debug.keystore --ks-pass pass:android \
  --ks-key-alias androiddebugkey --key-pass pass:android \
  --out base-patched-signed.apk base-patched-unsigned.apk

# Then install
adb install base-patched-signed.apk
```

## Technical Notes

### Why this approach works:
1. **JNI Function Replacement:** By replacing entire function bodies with immediate success returns, we bypass all signature validation logic regardless of implementation details or obfuscation.

2. **Minimal Code Changes:** Only 8 bytes modified per function, reducing the risk of breaking dependencies or causing instability.

3. **Architecture-Specific:** Patches target ARM64 (arm64-v8a) which is the standard for modern Android devices (Android 5.0+).

### Limitations:
- Other architectures (arm, x86, x86_64) remain unpatched in assets but shouldn't matter for modern devices
- Runtime Java/Kotlin checks (if any) not addressed
- Server-side integrity validation (if any) not bypassed
- May violate terms of service

## Testing Recommendations

1. Install on emulator or test device
2. Monitor logcat for signature-related errors:
   ```bash
   adb logcat | grep -i "signature\|integrity\|tamper\|invalid"
   ```
3. Verify app functionality post-installation
4. Check for crash logs: `adb logcat | grep "FATAL EXCEPTION"`

## Status

✅ Patches applied successfully
✅ APK repacked without errors
⏸️  Awaiting signature and installation testing
