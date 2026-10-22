# Research setup: next steps

Captured 2026-09-05. See `device-inventory.md`, `toki-compatibility.md`, and `experiment-plan.md` for the underlying observations and source links.

## What was verified

- ADB at `C:\Users\Youcef\Desktop\platform-tools\adb.exe` works; the phone is connected and authorized.
- Device is Samsung Galaxy A02 `SM-A022F`, Android 11/API 30, build `A022FXXS3BWH1`, security patch 2023-09-01, 32-bit ARM ABI only, locked bootloader, no `su`.
- No matching Toki, TikTok, LSPosed, or Magisk package name was returned by the read-only package search.
- Public Toki source was cloned into `research/upstream` at commit `5551d7431f1658de6cad2c3a7f8f878dad5135cd` and audited. The live checkout was not altered by this clone.
- Toki's code changes values within a scoped TikTok process; it does not change the SIM itself or the network IP. The location hook includes a mock-location-marker suppression path that this experiment plan excludes.
- Android 11 meets Toki's stated minimum API in principle. Device-specific support is unproven.

## Missing build tools / blocker

| Tool/package | Current observation | Needed for this repository |
| --- | --- | --- |
| Git | Available (`C:\Program Files\Git\cmd\git.exe`) | Already satisfied |
| ADB/platform-tools | Available; desktop copy is v37.0.1 | Already satisfied |
| Java | `java` resolves to Oracle Java 24 | Upstream specifies JDK 21 to run Gradle; install/use JDK 21 rather than relying on unverified JDK 24 compatibility |
| Gradle wrapper | `gradlew.bat` exists; Gradle 9.7.1 distribution is not cached | Wrapper will download the exact distribution |
| Android SDK platform | API 35 present | Android platform 37 required |
| Android Build Tools | 35.0.0, 35.0.1, 36.0.0 present | Build Tools 37.0.0 required |
| SDK command-line tools | `cmdline-tools` not found | Needed for a lightweight `sdkmanager` workflow |

An attempted `gradlew.bat --version` failed during HTTPS certificate validation. The endpoint certificate reported `NotBefore: 2026-09-11`, while the Windows clock at the time was 2026-09-05. Do not disable certificate validation or use an insecure download workaround. Retry after confirming the PC clock and that the official download endpoint presents a currently valid certificate.

## Proposed setup and disk-space estimate

No dependencies or system configuration were changed. Before doing that, the proposed light setup is:

1. Install a JDK 21 distribution and select it for this project only.
2. Install Android SDK command-line tools, platform 37, and Build Tools 37.0.0 through the official SDK Manager.
3. Let the Gradle wrapper download Gradle 9.7.1 and the project resolve dependencies from its declared official repositories.
4. Build a debug APK after the certificate/date issue is resolved. Do not install the APK until the user confirms whether they want the settings app alone; its hooks will not operate without a working API-102 framework.

Estimated additional disk space: **about 1.5–2.5 GB** for JDK 21, command-line tools, SDK platform/build tools, Gradle distribution, and a cold dependency cache. This is a planning estimate, not a package-manager measurement; actual Gradle/Maven cache usage depends on downloads. No emulator or Android Studio is needed for the requested physical-device workflow.

## Phone suitability and decision gates

The phone is suitable for read-only ADB inventory and, after a debug APK is built, ordinary app installation. It is **not yet suitable for a live Toki/TikTok hook experiment**: it is locked and unrooted, lacks the framework and TikTok, has unknown CSC/OEM menu status, and has no verified exact-build root path. The official LSPosed channel announced API 102 support in v2.1.0; arm32 support appears plausible from upstream architecture metadata but has not been tested on this model/build.

Safest next action: check **Settings → Developer options → OEM unlocking** manually and report whether the switch is present and its state; also report the installed CSC/sales code if visible in the phone's software information. Do not unlock anything yet. Samsung's official FAQ recommends contacting regional Samsung support for bootloader questions; generic Android documentation warns that unlock wipes data. Samsung documents that a tripped Knox Warranty Bit is irreversible and disables Knox-dependent services.

Explicit approval is required before unlocking, factory reset, rooting, flashing/modifying any partition, or disabling security controls. Exact firmware/CSC and a device-specific procedure must be verified first. No firmware has been downloaded.

## Sources

- [Toki build requirements and usage](https://github.com/MeiYongAI/Toki/blob/main/README.md)
- [Official LSPosed channel](https://t.me/s/LSPosed) and [LSPosed source](https://github.com/LSPosed/LSPosed)
- [AOSP bootloader unlock data-wipe requirements](https://source.android.com/docs/core/architecture/bootloader/locking_unlocking)
- [Samsung bootloader FAQ](https://developer.samsung.com/faq)
- [Samsung Knox Warranty Bit impact](https://docs.samsungknox.com/admin/knox-admin-portal/kbas/kba-360039680233/)
