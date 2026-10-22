# Toki repository and compatibility audit

Captured 2026-09-05. Public upstream was cloned read-only to `research/upstream`; clone HEAD is `5551d7431f1658de6cad2c3a7f8f878dad5135cd`. The clone is separate from the existing checkout. No upstream files were edited.

## Project and declared requirements

Toki is an Android settings app and an LSPosed module that hooks the **official TikTok process**. The UI uses Jetpack Compose / Material 3. The manifest identifies a module settings activity and launcher alias; it declares `xposedminversion=102`. The modern module metadata includes `java_init.list`, `module.prop`, and a scope list containing `com.zhiliaoapp.musically` and `com.ss.android.ugc.trill`.

The upstream README documents:

- Android 9 / API 28 minimum; `minSdk=28`, `targetSdk=35`, `compileSdk=37`.
- A working LSPosed installation that implements **libxposed API 102**.
- Official TikTok clients only; tested/adapted versions 47.1.4, 47.0.3, and 46.8.3.
- Build with JDK 21 (Java source and target level 17), Gradle wrapper 9.7.1, Android Gradle Plugin 9.4.0, Kotlin Compose plugin 2.2.10, Android SDK platform 37 and Build Tools 37.0.0. Dependencies resolve from Google Maven, Maven Central, and the Gradle Plugin Portal.
- MIT license. Release metadata and version notes are in `CHANGELOG.md` and GitHub Releases. Upstream warns the project uses AI-generated code and may contain errors.

The upstream main/README and changelog contain entries dated **2026-10-08**, later than this report date. Treat this snapshot's future-dated release metadata as a source-date inconsistency and verify the intended release/tag before building or installing it. The clone commit is recorded above so the inspected source can be identified exactly.

## Region-related code paths

| Feature | Source | What code does in the hooked app process |
| --- | --- | --- |
| SIM / network region | `app/src/main/java/io/github/meiyongai/toki/hook/SimHook.kt`, presets in `model/RegionPresets.kt` | Intercepts `TelephonyManager` getters for SIM/network country ISO, operator codes/names, SIM state, and related values. It returns configured preset data to the target process; it does not reprogram the physical SIM or cellular network. |
| Language / locale | `hook/LocaleHook.kt` | Intercepts Java locale reads for the target process. Source comments explicitly avoid changing the global process/native text-layout locale and Android Resources configuration. It is not a system-wide language change. |
| Time zone | `hook/TimeZoneHook.kt` | Intercepts Java and Android ICU default time-zone reads and supplies a preset or configured zone inside the target process. It does not change the phone's system clock or system time-zone setting. |
| Location | `hook/GpsHook.kt` | Intercepts `Location` coordinate getters and `LocationManager.getLastKnownLocation` inside the target process. It does not alter the phone's global location setting or GNSS hardware output. The source also returns `false` from `Location.isFromMockProvider()` while enabled; that is detector-evasion behavior, is not independently verified, and is excluded from the proposed experiment. |
| Creator region display | `hook/AuthorLocationHook.kt` | Reads TikTok's author region value and formats it with a flag/code prefix in the displayed name. It does not determine or change the viewer's region. |

These hooks only run when the module is loaded into the selected TikTok package. The reviewed code does not change the device's public IP address. A returned app-level value is not proof that TikTok's backend classified the account or viewer as being in that country.

## Android 11 and this phone

**In principle:** Android 11/API 30 is above Toki's declared API 28 minimum. The LSPosed project documents Android 8.1–14 support for its older published framework line; the official LSPosed channel later announced v2.1.0 with libxposed API 102. Framework and API documents therefore provide a plausible Android 11 path.

**Device-specific status:** not verified. The A02 is reported as 32-bit ARM only. LSPosed source/build metadata includes `armeabi-v7a`; the official announcement for v2.0.3 says it removed 32-bit **x86**, not ARM. This supports architectural plausibility, but no LSPosed API-102 build has been installed or tested on this A02, and a published framework ABI list is not proof of this Samsung firmware working. TikTok is not installed, so its version/variant and ABI compatibility are also unknown.

## SM-A022F bootloader/root evidence

ADB confirms a locked bootloader (`flash.locked=1`) and firmware string `A022FXXS3BWH1`; it does **not** establish whether this particular regional/carrier device exposes OEM unlocking. `ro.oem_unlock_supported=1` is a generic support property, not a user-menu or unlockability confirmation. CSC was not collected.

Samsung's developer FAQ does not publish an unlock procedure and directs users to regional Samsung support. Public third-party posts/tutorials exist for SM-A022F, but the ones found are not an official, variant-and-build-matched procedure with enough evidence to validate this exact firmware/CSC. No exact recovery image or reliable recovery-based root procedure was verified. Do not use A02s materials for this A02 or flash files selected from a model name alone.

The generic Android bootloader contract says unlocking wipes user data. Samsung documents the Knox Warranty Bit as a one-time fuse; once tripped it cannot be reverted, and Knox-dependent features such as Secure Folder/Samsung Pay may stop working. The exact feature impact on this individual A02 has not been tested. A wrong image or binary/CSC mismatch can also cause a boot loop or require recovery with exact stock firmware. No firmware was downloaded and no flash/unlock action was attempted.

## Evidence gaps

- OEM Unlocking menu state, Samsung region/CSC, SIM/carrier restrictions, and Download Mode unlock eligibility.
- A credible root procedure matching `SM-A022F`, current build `A022FXXS3BWH1`, binary 3, and the phone's CSC.
- API-102 framework release details for this exact Samsung configuration, plus real ARM32 install/test evidence.
- An installed official TikTok version among Toki's documented adaptations.
- Live validation of any region hook or TikTok/backend country classification.

## Sources

- [Toki upstream repository](https://github.com/MeiYongAI/Toki), [README](https://github.com/MeiYongAI/Toki/blob/main/README.md), [releases](https://github.com/MeiYongAI/Toki/releases), and inspected clone commit above.
- [LSPosed official repository and older Android support declaration](https://github.com/LSPosed/LSPosed); [official LSPosed Telegram channel](https://t.me/s/LSPosed), which announced API 102 support in v2.1.0 and reports removal of 32-bit x86 in v2.0.3; [LSPosed modern API module documentation](https://github.com/LSPosed/LSPosed/wiki/Develop-Xposed-Modules-Using-Modern-Xposed-API); [libxposed API 102 RFC](https://github.com/libxposed/api/pull/62).
- [Samsung Developer FAQ: bootloader questions](https://developer.samsung.com/faq) and [Samsung Knox Warranty Bit documentation](https://docs.samsungknox.com/admin/knox-admin-portal/kbas/kba-360039680233/).
- [AOSP bootloader unlocking contract](https://source.android.com/docs/core/architecture/bootloader/locking_unlocking) and [verified boot device states](https://source.android.com/docs/security/features/verifiedboot/device-state).
- URLs checked for this report on 2026-09-05. Community-only exact-model search results were treated as leads, not validation.
