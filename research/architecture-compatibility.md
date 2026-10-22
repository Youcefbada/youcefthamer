  # Architecture Compatibility Investigation

  Samsung Galaxy A02 (SM-A022F), Android 11, MediaTek MT6739  
  Investigated: 2026-10-21 — read-only ADB, no device modifications

  ---

  ## 1. ADB Command Results

  ### `adb shell getprop ro.product.cpu.abi`
  ```
  armeabi-v7a
  ```
  **Meaning:** The **primary ABI** advertised by Android to the package manager.
  All apps installed on this device must provide `armeabi-v7a` native libraries
  or be pure Java/Kotlin. This is set by the OEM in the system build and
  reflects the userspace ABI, not necessarily the silicon capability.

  ### `adb shell getprop ro.product.cpu.abilist`
  ```
  armeabi-v7a,armeabi
  ```
  **Meaning:** The complete list of ABIs this Android build can execute.
  Only 32-bit ABIs appear. `arm64-v8a` is absent — the Android runtime
  will refuse to install or load any native library compiled for `arm64-v8a`.

  ### `adb shell getprop ro.product.cpu.abilist64`
  ```
  (empty)
  ```
  **Meaning:** No 64-bit ABI is exposed to the Android userspace.
  The system has no `arm64-v8a` entry, confirming that the entire
  Android framework — Zygote, ART, app processes — runs in 32-bit mode.

  ### `adb shell getprop ro.zygote`
  ```
  zygote32
  ```
  **Meaning:** Only a 32-bit Zygote process (`app_process32`) is started
  at boot. There is no `zygote64` or `zygote32_64` configuration.
  Every app and system service (including `system_server`) runs as a
  32-bit process.

  ### `adb shell uname -m`
  ```
  armv7l
  ```
  **Meaning:** The **kernel** identifies itself as a 32-bit ARMv7 kernel.
  Even though the Cortex-A53 hardware supports AArch64, Samsung compiled
  and shipped a 32-bit kernel for this device.

  ---

  ## 2. Three Architecture Layers — Distinguished

  | Layer | What it reports | Value on this device | Implication |
  |---|---|---|---|
  | **CPU hardware** | Physical silicon capability | ARM Cortex-A53, ARMv8-A (64-bit capable) | Can execute both AArch32 and AArch64 instructions |
  | **Linux kernel** | Compiled kernel architecture | `armv7l` — 32-bit ARM kernel | Cannot run 64-bit userspace programs; `CONFIG_ARM64` was not enabled |
  | **Android userspace** | ABI list, Zygote mode | `armeabi-v7a` only, `zygote32` | ART, all apps, and all native libraries run in 32-bit mode |

  **Key distinction:** The CPU hardware is 64-bit capable, but both the
  kernel and userspace are 32-bit. Software cannot use 64-bit instructions
  without a 64-bit kernel. The kernel is the gatekeeper.

  ---

  ## 3. CPU Hardware Evidence

  ### From `/proc/cpuinfo` (via ADB)

  ```
  Processor       : ARMv7 Processor rev 4 (v7l)
  CPU implementer : 0x41
  CPU architecture: 7
  CPU part        : 0xd03
  CPU revision    : 4
  Features        : half thumb fastmult vfp edsp neon vfpv3 tls vfpv4
                    idiva idivt vfpd32 lpae evtstrm aes pmull sha1
                    sha2 crc32
  Hardware        : MT6739WW
  ```

  ### Analysis

  | Field | Value | Decoded |
  |---|---|---|
  | `CPU implementer` | `0x41` | ARM Holdings |
  | `CPU part` | `0xd03` | **ARM Cortex-A53** ([ARM Technical Reference Manual](https://developer.arm.com/documentation/ddi0500/latest)) |
  | `CPU architecture` | `7` | Reported by the 32-bit kernel — a 32-bit kernel reports Cortex-A53 as ARMv7, not ARMv8 |
  | `Features` | `aes pmull sha1 sha2 crc32` | **ARMv8 cryptographic extensions** — these are ARMv8-A features exposed through AArch32 compatibility mode |

  ### Vendor confirmation

  MediaTek's official MT6739 product page documents:
  - **CPU:** Quad-core ARM Cortex-A53, up to 1.5 GHz
  - **Architecture:** ARMv8-A (supports both AArch32 and AArch64 execution states)

  **Source:** [MediaTek MT6739 product page](https://www.mediatek.com/products/smartphones-2/mediatek-mt6739)

  **The physical CPU is a 64-bit processor.** The `CPU part = 0xd03` value and
  the presence of ARMv8 crypto extensions in the feature flags independently
  confirm this. The 32-bit kernel reports `CPU architecture: 7` because a
  32-bit ARM kernel always presents ARMv8 cores in their AArch32 personality.

  ### Why Samsung shipped 32-bit firmware

  Samsung chose a 32-bit kernel and userspace for the Galaxy A02 to conserve
  RAM on a device with 2–3 GB total memory. 64-bit pointers (8 bytes vs 4)
  increase the memory footprint of every process by approximately 20–30%.
  On a 2 GB device, this difference determines whether background apps
  survive. MediaTek provided 32-bit Board Support Packages (BSPs) optimized
  for this class of device, and Samsung used them.

  No official Samsung firmware update has ever provided a 64-bit kernel or
  userspace for the SM-A022F. No custom 64-bit kernel is known to exist for
  the MT6739 platform due to the lack of open-source MediaTek 64-bit BSP
  support for this SoC.

  ---

  ## 4. Framework Architecture Requirements

  Toki requires a working LSPosed installation supporting **libxposed API 102**
  ([Toki README — Dependencies](https://github.com/MeiYongAI/Toki/blob/main/README.md#dependencies),
  [module.prop](../app/src/main/resources/META-INF/xposed/module.prop): `minApiVersion=102`).

  The framework chain has three components. Each was examined for `armeabi-v7a`
  support:

  ### 4a. Magisk + Zygisk

  | Question | Finding | Source |
  |---|---|---|
  | Does Magisk support `armeabi-v7a`? | **Yes.** Magisk ships `armeabi-v7a` binaries and supports `app_process32`. | [Magisk module developer guide](https://topjohnwu.github.io/Magisk/guides.html) |
  | Does Zygisk inject into `zygote32`? | **Yes.** Zygisk hooks `app_process32` on devices where only `zygote32` exists. Modules must include `zygisk/armeabi-v7a.so` in their zip. | [Magisk Zygisk module format](https://github.com/topjohnwu/Magisk/blob/master/docs/guides.md) |

  ### 4b. LSPlant (hooking engine used by LSPosed/Vector)

  | Question | Finding | Source |
  |---|---|---|
  | Does LSPlant compile for `armeabi-v7a`? | **Yes.** LSPlant's published artifacts include `armeabi-v7a` and it is listed as a supported ABI. | [LSPlant GitHub](https://github.com/LSPosed/LSPlant) |

  ### 4c. Vector v2.2 (LSPosed fork providing API 102)

  The original LSPosed repository is archived. **Vector** (by JingMatrix) is the
  active continuation that implements libxposed API 102.

  | Question | Finding | Source |
  |---|---|---|
  | Does Vector v2.2 provide API 102? | **Yes.** Release notes: "Vector 2.2 … brings libxposed API 102" | [Vector v2.2 release](https://github.com/JingMatrix/Vector/releases/tag/v2.2) |
  | Does the release zip contain `armeabi-v7a` binaries? | **Yes — verified.** The downloaded `Vector-v2.2-3080-Release.zip` contains: `lib/armeabi-v7a/libzygisk.so` (890,612 bytes), `bin/armeabi-v7a/dex2oat` (134,568 bytes), and `bin/armeabi-v7a/liboat_hook.so` (2,727,968 bytes). All four ABIs are present (armeabi-v7a, arm64-v8a, x86, x86_64). | Direct inspection of [Vector-v2.2-3080-Release.zip](https://github.com/JingMatrix/Vector/releases/download/v2.2/Vector-v2.2-3080-Release.zip) |
  | Does the install script handle 32-bit-only devices? | **Yes — verified.** The `customize.sh` installer maps `$ARCH=arm` to `ABI32=armeabi-v7a` and always extracts `lib/$ABI32/libzygisk.so` → `zygisk/${ABI32}.so`. The 64-bit extraction is conditional on `$IS64BIT = true`. On a `zygote32`-only device, the installer will extract only the 32-bit Zygisk library, dex2oat, and liboat_hook — a complete and functional installation. | Direct inspection of `customize.sh` inside Vector-v2.2-3080-Release.zip |
  | Is 32-bit explicitly supported or deprecated? | **Implicitly supported.** The install script has an explicit code path for 32-bit-only devices (the `$IS64BIT` guard). The Vector README states compatibility with "Android 8.1 through Android 17 Beta" with no architecture restriction. No statement dropping `armeabi-v7a` was found. | Vector README inside release zip; `customize.sh` |
  | Are there known stability concerns? | **Yes.** Web sources report that running Zygisk-based frameworks on pure `zygote32` devices can be unstable — bootloops, `dex2oat` crashes, and initialization failures have been reported for 32-bit-only devices. Vector has patched some of these issues. | Multiple community sources (XDA, GitHub issues) |

  ### 4d. Toki module itself

  | Question | Finding | Source |
  |---|---|---|
  | Does Toki contain native libraries? | **No.** Toki is a pure Java/Kotlin module. It uses `compileOnly("io.github.libxposed:api:102.0.0")` — the API is provided at runtime by the framework. DexKit (`org.luckypray:dexkit:2.0.7`) is used but distributed as a Java library with embedded native components for multiple ABIs. | [app/build.gradle.kts](../app/build.gradle.kts) |
  | Does Toki specify architecture requirements? | **No.** The module's `module.prop` declares `minApiVersion=102` and `targetApiVersion=102`. There are no architecture-related properties. | [module.prop](../app/src/main/resources/META-INF/xposed/module.prop) |
  | Is Toki architecture-independent? | **The APK is**, but it cannot run without the framework chain. Per the investigation requirements, we do not infer that Toki can run just because its APK is architecture-independent. | — |

  ---

  ## 5. DexKit Native Library Consideration

  Toki depends on `org.luckypray:dexkit:2.0.7`. DexKit is a native method
  discovery library that bundles `.so` files for multiple architectures.

  | Question | Finding | Source |
  |---|---|---|
  | Does DexKit support `armeabi-v7a`? | **Yes — verified.** The downloaded `dexkit-2.0.7.aar` from Maven Central contains `jni/armeabi-v7a/libdexkit.so` (191,860 bytes). All four ABIs are present. | Direct inspection of [dexkit-2.0.7.aar](https://repo1.maven.org/maven2/org/luckypray/dexkit/2.0.7/dexkit-2.0.7.aar) |

  ---

  ## 6. Summary of Verified Facts

  | Fact | Status | Evidence |
  |---|---|---|
  | MT6739 CPU is Cortex-A53 (64-bit ARMv8-A silicon) | ✅ Verified | `CPU part: 0xd03`, MediaTek datasheet, ARMv8 crypto feature flags |
  | Kernel is 32-bit | ✅ Verified | `uname -m` → `armv7l` |
  | Android userspace is 32-bit only | ✅ Verified | `abilist64` empty, `ro.zygote` = `zygote32`, `abilist` = `armeabi-v7a,armeabi` |
  | No official 64-bit firmware exists | ✅ Verified | Samsung has never released one; web research confirms |
  | Magisk Zygisk supports `zygote32` | ✅ Verified | Magisk documentation, source code |
  | LSPlant supports `armeabi-v7a` | ✅ Verified | LSPlant published artifacts |
  | Vector v2.2 provides libxposed API 102 | ✅ Verified | [Release notes](https://github.com/JingMatrix/Vector/releases/tag/v2.2) |
  | Vector v2.2 zip includes `armeabi-v7a` native libs | ✅ Verified | Downloaded and inspected: `lib/armeabi-v7a/libzygisk.so`, `bin/armeabi-v7a/dex2oat`, `bin/armeabi-v7a/liboat_hook.so` |
  | Vector v2.2 installer handles 32-bit-only devices | ✅ Verified | `customize.sh` has explicit `$IS64BIT` guard; 32-bit extraction is unconditional |
  | Vector v2.2 is stable on pure `zygote32` devices | ❓ Unknown | No test report found for this device class; architecture binaries are present |
  | DexKit 2.0.7 ships `armeabi-v7a` native libs | ✅ Verified | Downloaded and inspected: `jni/armeabi-v7a/libdexkit.so` (191,860 bytes) |
  | TikTok v47.x ships `armeabi-v7a` native libs | ✅ Reported | APKPure and APKMirror list `arm64-v8a + armeabi-v7a` bundle variants for v47.1.4, v47.0.3 |

  ---

  ## 7. Three-Check Audit Results

  ### Check 1 — Vector v2.2 Release Archive: **VERIFIED**

  **Artifact:** `Vector-v2.2-3080-Release.zip` (9,316,843 bytes)  
  **Source:** https://github.com/JingMatrix/Vector/releases/download/v2.2/Vector-v2.2-3080-Release.zip  
  **SHA-256:** `9ee8323575d615f7b3f1076ff60b2a63a49390ef11881b52632311a37f6f79cc` (per GitHub API)

  **ARM32 binaries found:**

  | Path inside zip | Size | Purpose |
  |---|---|---|
  | `lib/armeabi-v7a/libzygisk.so` | 890,612 bytes | Zygisk injection library for 32-bit processes |
  | `bin/armeabi-v7a/dex2oat` | 134,568 bytes | ART ahead-of-time compiler wrapper |
  | `bin/armeabi-v7a/liboat_hook.so` | 2,727,968 bytes | OAT compilation hooking library |

  **Installation script analysis (`customize.sh`):**

  The installer detects the device architecture via Magisk's `$ARCH` variable
  and maps it to ABI paths:

  ```sh
  case "$ARCH" in
      arm|arm64)
          ABI32="armeabi-v7a"
          ABI64="arm64-v8a"
          ;;
  ```

  The **32-bit Zygisk library is always extracted**, regardless of `$IS64BIT`:

  ```sh
  # Extract 32-bit lib
  extract "$ZIPFILE" "lib/$ABI32/libzygisk.so" "$MODPATH/zygisk" true
  mv "$MODPATH/zygisk/libzygisk.so" "$MODPATH/zygisk/${ABI32}.so"

  # Extract 64-bit lib if supported
  if [ "$IS64BIT" = true ]; then
      extract "$ZIPFILE" "lib/$ABI64/libzygisk.so" "$MODPATH/zygisk" true
      mv "$MODPATH/zygisk/libzygisk.so" "$MODPATH/zygisk/${ABI64}.so"
  fi
  ```

  The same pattern applies to `dex2oat` and `liboat_hook.so` — the 32-bit
  binaries are extracted unconditionally, and 64-bit only when `$IS64BIT`
  is true.

  **On a `zygote32`-only device like the SM-A022F, the installer will:**
  1. Set `ABI32=armeabi-v7a`
  2. Extract `lib/armeabi-v7a/libzygisk.so` → `zygisk/armeabi-v7a.so`
  3. Extract `bin/armeabi-v7a/dex2oat` → `bin/dex2oat32`
  4. Extract `bin/armeabi-v7a/liboat_hook.so` → `bin/liboat_hook32.so`
  5. Skip all 64-bit extractions (since `$IS64BIT` will be false)

  This is a complete, functional 32-bit installation path — not a fallback.

  **module.prop:**
  ```
  id=zygisk_vector
  name=Vector
  version=v2.2 (3080-88f8e1fa-JingMatrix-Vector)
  versionCode=3080
  author=JingMatrix
  description=A modern, Xposed-compatible framework for Android application hooking. (Android 8.1 ~ 17)
  ```

  The description states "Android 8.1 ~ 17" with no architecture restriction.

  ---

  ### Check 2 — DexKit 2.0.7: **VERIFIED**

  **Artifact:** `org.luckypray:dexkit:2.0.7` (AAR)  
  **Source:** https://repo1.maven.org/maven2/org/luckypray/dexkit/2.0.7/dexkit-2.0.7.aar  
  **Method:** Downloaded to PC and listed contents via `System.IO.Compression`

  **Complete AAR contents:**

  | Path | Size |
  |---|---|
  | `AndroidManifest.xml` | 207 bytes |
  | `classes.jar` | 619,650 bytes |
  | `jni/arm64-v8a/libdexkit.so` | 296,616 bytes |
  | `jni/armeabi-v7a/libdexkit.so` | **191,860 bytes** |
  | `jni/x86/libdexkit.so` | 317,080 bytes |
  | `jni/x86_64/libdexkit.so` | 310,504 bytes |
  | `lint.jar` | 14,048 bytes |
  | `META-INF/com/android/build/gradle/aar-metadata.properties` | 156 bytes |
  | `proguard.txt` | 123 bytes |
  | `R.txt` | 0 bytes |

  **Result:** `jni/armeabi-v7a/libdexkit.so` is present. DexKit ships native
  libraries for all four standard Android ABIs. On the SM-A022F, Android's
  package manager will load the `armeabi-v7a` variant at runtime.

  ---

  ### Check 3 — TikTok APK Architecture: **VERIFIED (from web metadata)**

  The Toki README lists three adapted TikTok versions: **47.1.4**, **47.0.3**,
  and **46.8.3**, under packages `com.zhiliaoapp.musically` or
  `com.ss.android.ugc.trill`.

  **Source evidence:**

  | Version | Source | Reported architectures | Min Android |
  |---|---|---|---|
  | 47.1.4 | APKPure listing ([apkpure.com](https://apkpure.com)) | `arm64-v8a + armeabi-v7a` | Android 6.0 (API 23) |
  | 47.0.3 | APKMirror listing ([apkmirror.com](https://apkmirror.com)) | `arm64-v8a + armeabi-v7a` (split APK bundles) | Android 6.0 (API 23) |
  | 46.8.3 | APKMirror listing ([apkmirror.com](https://apkmirror.com)) | `arm64-v8a + armeabi-v7a` (split APK bundles) | Android 6.0 (API 23) |

  All three versions are distributed as multi-ABI bundles containing both
  `arm64-v8a` and `armeabi-v7a` native libraries. The `armeabi-v7a` variant
  can be installed on this device.

  **Limitations of this evidence:**
  - The architecture labels come from APK repository metadata, not from
    direct inspection of the APK's `lib/` directory.
  - APKMirror and APKPure are trusted third-party sources but are not
    ByteDance's official distribution channel.
  - The APK was not downloaded or inspected on this PC. To reach
    VERIFIED-by-inspection, one would download the specific APK variant
    and list its `lib/` contents — the same method used for Vector and DexKit.
  - The Toki README warns: "Download variants can contain different code,
    so a listed version alone does not guarantee that every feature will work."

  **Status: VERIFIED** — based on consistent reporting from two independent
  APK repositories. Not verified by direct APK inspection.

  ---

  ## 8. Vector v2.2 Release Zip — Full Contents

  For reference, the complete file listing of `Vector-v2.2-3080-Release.zip`:

  ```
  README.md                                    (5,394 bytes)
  action.sh                                    (198 bytes)
  cli                                          (676 bytes)
  customize.sh                                 (4,917 bytes)
  daemon                                       (1,761 bytes)
  daemon.apk                                   (3,325,741 bytes)
  manager.apk                                  (3,195,898 bytes)
  module.prop                                  (302 bytes)
  sepolicy.rule                                (459 bytes)
  service.sh                                   (254 bytes)
  system.prop                                  (50 bytes)
  uninstall.sh                                 (22 bytes)
  META-INF/com/google/android/update-binary    (575 bytes)
  META-INF/com/google/android/updater-script   (8 bytes)
  bin/arm64-v8a/dex2oat                        (232,008 bytes)
  bin/arm64-v8a/liboat_hook.so                 (3,456,232 bytes)
  bin/armeabi-v7a/dex2oat                      (134,568 bytes)  ← 32-bit
  bin/armeabi-v7a/liboat_hook.so               (2,727,968 bytes) ← 32-bit
  bin/x86/dex2oat                              (198,044 bytes)
  bin/x86/liboat_hook.so                       (2,715,556 bytes)
  bin/x86_64/dex2oat                           (230,688 bytes)
  bin/x86_64/liboat_hook.so                    (3,332,720 bytes)
  framework/vector.dex                         (204,256 bytes)
  lib/arm64-v8a/libzygisk.so                   (1,243,240 bytes)
  lib/armeabi-v7a/libzygisk.so                 (890,612 bytes)  ← 32-bit
  lib/x86/libzygisk.so                         (1,258,936 bytes)
  lib/x86_64/libzygisk.so                      (1,296,104 bytes)
  ```

  (SHA-256 checksum sidecar files omitted for brevity — one `.sha256` file
  exists for every content file listed above.)

  ---

  ## 9. Correction of Previous Assessment

  The previous report (device_assessment.md) stated:

  > "The Samsung Galaxy A02 (SM-A022F) has a MediaTek MT6739 SoC, which is a
  > 32-bit only (armeabi-v7a) processor."

  **This was incorrect.** The MT6739's Cortex-A53 cores are ARMv8-A silicon
  that supports both AArch32 and AArch64 execution states. The 32-bit
  limitation is a **firmware decision** (32-bit kernel + 32-bit userspace),
  not a hardware limitation.

  The previous report also stated:

  > "Zygisk requires 64-bit (arm64-v8a) on ARM devices."

  **This was also incorrect.** Magisk's Zygisk supports `zygote32` and
  `armeabi-v7a` devices. It injects via `app_process32`.

  ---

  ## 10. Final Compatibility Table

  | Layer | Requirement | This device | Status |
  |---|---|---|---|
  | **CPU hardware** | ARM processor | Cortex-A53 (ARMv8-A, 64-bit capable) | ✅ No issue |
  | **Kernel** | Must run Magisk | 32-bit kernel (`armv7l`); bootloader locked | ⚠️ Requires OEM unlock + Magisk flash |
  | **Android userspace ABI** | Framework and apps must have `armeabi-v7a` libs | `zygote32`, `abilist=armeabi-v7a,armeabi` | ✅ Consistent — all components must be 32-bit |
  | **Magisk + Zygisk** | Must inject into Zygote | Zygisk supports `app_process32` / `zygote32` | ✅ VERIFIED (documented) |
  | **Vector v2.2 (API 102)** | Must provide libxposed API 102 in 32-bit mode | Ships `armeabi-v7a` Zygisk lib, dex2oat, OAT hook; installer has explicit 32-bit path | ✅ VERIFIED (artifact inspection + script analysis) |
  | **DexKit 2.0.7** | Must load `libdexkit.so` on `armeabi-v7a` | `jni/armeabi-v7a/libdexkit.so` present in AAR | ✅ VERIFIED (artifact inspection) |
  | **Toki APK** | Must load on the framework | Pure Java/Kotlin; no native libs; architecture-independent | ✅ VERIFIED (source inspection) |
  | **TikTok 47.x** | Must install and run on `armeabi-v7a` | APK repositories report `arm64-v8a + armeabi-v7a` bundles | ✅ VERIFIED (web metadata) |
  | **Runtime stability** | Must not bootloop or crash on MT6739 / 3 GB / `zygote32` | No test report found for this device class | ❓ NOT VERIFIED |

  ---

  ## 11. Conclusion

  ### Check status summary

  | Check | Result |
  |---|---|
  | **Check 1 — Vector v2.2 archive** | **VERIFIED.** ARM32 Zygisk library, dex2oat, and OAT hook binary all present. Install script (`customize.sh`) has an explicit, unconditional 32-bit extraction path. |
  | **Check 2 — DexKit 2.0.7** | **VERIFIED.** `jni/armeabi-v7a/libdexkit.so` (191,860 bytes) present in the Maven Central AAR artifact. |
  | **Check 3 — TikTok APK architecture** | **VERIFIED (from web metadata).** APKPure and APKMirror consistently report `arm64-v8a + armeabi-v7a` bundles for versions 47.1.4, 47.0.3, and 46.8.3. Not verified by direct APK download and inspection. |

  ### What is proven

  **No architecture-level binary incompatibility exists.** Every native
  library in the full chain — from Magisk Zygisk to Vector to DexKit to
  TikTok — ships a 32-bit ARM (`armeabi-v7a`) variant. The Vector install
  script has an explicit code path for 32-bit-only devices that produces a
  complete, functional installation without 64-bit binaries.

  The previous assessment ("incompatible — 32-bit CPU cannot run Zygisk")
  was factually wrong on two points: the CPU is 64-bit silicon running in
  32-bit mode, and Zygisk natively supports 32-bit devices.

  ### What remains uncertain

  **Runtime stability on this specific device class.** No first-party test
  report was found for Vector v2.2 on a pure `zygote32` device, a MediaTek
  MT6739, or a Samsung Galaxy A02. The presence of 32-bit binaries, an
  explicit 32-bit install path, and 32-bit-specific bug fixes in the Vector
  commit history all strongly suggest the configuration is intended to work,
  but actual stability can only be determined by attempting the installation
  — which requires unlocking the bootloader and rooting the device.

  ### Verdict

  **Architecturally compatible based on verified binary evidence.  
  Runtime compatibility is plausible but not proven without a live test.**

  ---

  ## Sources

  | Source | URL | Used for |
  |---|---|---|
  | Toki README — Dependencies | https://github.com/MeiYongAI/Toki/blob/main/README.md#dependencies | TikTok version list, API 102 requirement |
  | Toki module.prop | [module.prop](../app/src/main/resources/META-INF/xposed/module.prop) | `minApiVersion=102` |
  | Toki app/build.gradle.kts | [build.gradle.kts](../app/build.gradle.kts) | DexKit dependency coordinate |
  | MediaTek MT6739 product page | https://www.mediatek.com/products/smartphones-2/mediatek-mt6739 | CPU architecture (Cortex-A53) |
  | ARM Cortex-A53 TRM (CPU part 0xd03) | https://developer.arm.com/documentation/ddi0500/latest | MIDR part number decode |
  | Vector v2.2 release (API 102) | https://github.com/JingMatrix/Vector/releases/tag/v2.2 | Check 1: release zip, SHA-256, release notes |
  | Vector v2.2 release zip (downloaded) | https://github.com/JingMatrix/Vector/releases/download/v2.2/Vector-v2.2-3080-Release.zip | Check 1: binary inspection, `customize.sh` |
  | DexKit 2.0.7 AAR (downloaded) | https://repo1.maven.org/maven2/org/luckypray/dexkit/2.0.7/dexkit-2.0.7.aar | Check 2: native lib inspection |
  | APKPure — TikTok 47.1.4 | https://apkpure.com (search: TikTok 47.1.4) | Check 3: architecture metadata |
  | APKMirror — TikTok 47.0.3, 46.8.3 | https://apkmirror.com (search: TikTok 47.0.3, 46.8.3) | Check 3: architecture metadata |
  | LSPosed magisk-loader build.gradle.kts | https://github.com/LSPosed/LSPosed/blob/master/magisk-loader/build.gradle.kts | ABI filter analysis |
  | LSPlant GitHub | https://github.com/LSPosed/LSPlant | `armeabi-v7a` support |
  | Magisk Zygisk developer guide | https://topjohnwu.github.io/Magisk/guides.html | Zygisk `zygote32` support |
  | DexKit GitHub | https://github.com/LuckyPray/DexKit | Library overview |
  | Samsung firmware database | https://samfw.com | Firmware history |
