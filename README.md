# Android APK Anti-Tampering Bypass Patch

This repository contains a patched Android APK with anti-tampering protection disabled.

## What was patched

### 1. libclient.so (lib/arm64-v8a/)
Patched two JNI signature verification functions to always return `true` (1):
- `Java_com_eternal_xdsdk_SuperJNI_00024Companion_check` at offset `0x1625BC`
- `Java_com_eternal_xdsdk_SuperJNI_00024Companion_licence` at offset `0x161020`

**Patch applied:** Both functions replaced with ARM64 instructions:
```assembly
MOV X0, #1      ; Set return value to 1 (true)
RET             ; Return immediately
```

Hex bytes: `20 00 80 D2 C0 03 5F D6`

### 2. lib2f8c0b3257fcc345.so (assets/burriiiii/arm64/)
Disabled bytehook protection by nullifying the "Invalid access!" error message string at offset `0xC52A`.

This prevents the app from aborting when signature mismatches are detected by the bytehook framework.

## Files

- `base.apk` - Original APK (unchanged)
- `base-patched-unsigned.apk` - Patched APK with anti-tampering bypassed (unsigned)
- `patch_lib.py` - Script to patch libclient.so signature checks
- `patch_burriiiii.py` - Script to patch bytehook protection
- `repack_apk.py` - Script to repack APK from extracted directory

## How to sign the patched APK

The patched APK is currently **unsigned** and will not install on most devices without signing.

### Option 1: Using apksigner (Android SDK Build Tools)

```bash
# Generate a debug keystore (one time)
keytool -genkey -v -keystore debug.keystore -storepass android \
  -alias androiddebugkey -keypass android -keyalg RSA -keysize 2048 \
  -validity 10000 -dname "CN=Android Debug,O=Android,C=US"

# Sign the APK
apksigner sign --ks debug.keystore --ks-pass pass:android \
  --ks-key-alias androiddebugkey --key-pass pass:android \
  --out base-patched-signed.apk base-patched-unsigned.apk

# Verify the signature
apksigner verify base-patched-signed.apk
```

### Option 2: Using jarsigner (Java JDK)

```bash
# Generate keystore
keytool -genkey -v -keystore debug.keystore -alias mykey \
  -keyalg RSA -keysize 2048 -validity 10000

# Sign with jarsigner
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
  -keystore debug.keystore base-patched-unsigned.apk mykey

# Align the APK (optional but recommended)
zipalign -v 4 base-patched-unsigned.apk base-patched-signed.apk
```

### Option 3: Using uber-apk-signer

```bash
# Download uber-apk-signer
wget https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar

# Sign the APK (auto-generates debug key)
java -jar uber-apk-signer-1.3.0.jar --apks base-patched-unsigned.apk
```

## Installation

After signing, install via ADB:

```bash
adb install base-patched-signed.apk
```

Or transfer to device and install manually.

## Testing

To verify the patches work:

1. Install the patched APK
2. Check logcat for signature verification messages:
   ```bash
   adb logcat | grep -i "signature\|check\|licence\|verify\|invalid"
   ```
3. The app should start without crashes related to signature mismatches

## Technical Details

### Original Protection Mechanisms

1. **JNI Signature Checks** (`libclient.so`)
   - `SuperJNI.check()` - Verifies APK signature against expected value
   - `SuperJNI.licence()` - Validates app licensing/integrity
   - Both functions used Android's `PackageManager` APIs to read signatures

2. **Bytehook Protection** (`lib2f8c0b3257fcc345.so`)
   - Uses bytehook library to detect hooking frameworks (Frida, Xposed, etc.)
   - Monitors PLT/GOT modifications
   - Triggers "Invalid access!" abort on tampering detection

### Patch Strategy

Instead of trying to bypass checks conditionally, we force both JNI functions to:
- Skip all signature validation logic
- Immediately return success (1)
- Minimize execution time to avoid other checks

This approach is more reliable than NOP-ing individual checks because:
- It works regardless of obfuscation
- It doesn't depend on finding all check locations
- The functions are called from Java, so the return value is trusted

## Limitations

- Only arm64-v8a architecture is patched (the primary architecture in modern Android)
- Other architectures (arm, x86, x86_64) remain unpatched in assets
- Runtime checks in Java/Kotlin code (if any) are not addressed
- Network-based integrity checks (if any) are not patched

## Disclaimer

This tool is for educational and research purposes only. Modifying APK files may:
- Violate terms of service
- Be illegal in some jurisdictions
- Cause security vulnerabilities
- Result in account bans

Use at your own risk.
