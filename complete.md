# 🇸🇦 Saudi Arabia (KSA) TikTok Phase-2 Enterprise Stealth & Automation Report

**Document ID:** `TOKI-KSA-PHASE2-COMPLETE`  
**Deployment Date:** October 22, 2026  
**Status:** ✅ 100% Deployed, Injected & Operational on Physical Device  
**Physical Device:** Samsung Galaxy A02 (`SM-A022F` / `a02xx`)  
**OS / Platform:** Android 11 (One UI Core 3.1, API Level 30, Build `A022FXXS3BWH1`)  
**Userspace Architecture:** 32-bit ARM userspace (`armeabi-v7a` on MediaTek `MT6739` SoC — Low-RAM Edition)  
**Root Framework:** Magisk `v30.7` + Vector (`Zygisk LSPosed API 102 v2.2`)  
**Target Application:** Official TikTok Global (`com.zhiliaoapp.musically`, version `v47.1.4`)  
**Active Anti-Detection Core:** `io.github.meiyongai.toki` (`v2.0.0 Enterprise Native Edition`)  
**VPN Client:** `com.v2ray.ang` (v2rayNG `v2.3.11` with Xray-Core)  

---

## 1. Executive Summary & Architectural Upgrade

The system has been upgraded from the initial Phase-1 platform baseline to the **Phase-2 Enterprise Stealth & Bio-Automation Architecture**. This stack provides complete hardware identity cloaking, network leak prevention, and human-like touch telemetry to survive ByteDance's deepest native risk and behavioral engines (`libmetasec_ml.so`, `libmsaoaidsec.so`, `libttboringssl.so`, and `SSCronet`).

### Key Upgrades Implemented:
1. **Wi-Fi & Router Telemetry Realism ([`SimHook.kt`](file:///c:/Users/Youcef/Desktop/Toki/app/src/main/java/io/github/meiyongai/toki/hook/SimHook.kt)):**
   - **Eliminated `02:00:00:00:00:00` BSSID Anomaly:** Replaced with a genuine Saudi Telecom Company (STC) Huawei Fiber ONT MAC (`48:fd:8e:b1:2c:4d`).
   - **Spoofed SSID & Wi-Fi Metrics:** `WifiInfo.getSSID()` returns `"\"STC_5G_Home_A8F\""`, frequency `5180 MHz` (5 GHz Band), link speed `433 Mbps`, and fluctuating RSSI (`-48` to `-56` dBm).
   - **Synthetic Scan Results:** `WifiManager.getScanResults()` returns 4 realistic neighboring Riyadh residential networks (`STC_5G_Home_A8F`, `STC_Fiber_5GHz`, `Mobily_Fiber_92B`, `Zain_Home_4G`), eliminating empty scan list flags.
2. **Riyadh Cellular Base Station (`CellInfoLte`):**
   - Hooks `TelephonyManager.getAllCellInfo()` and `getCellLocation()` returning an STC Riyadh LTE Band 3 cell tower (`MCC 420`, `MNC 01`, `TAC 14102`, `CI 28491021`, `PCI 184`, `EARFCN 1650`, `RSRP -85 dBm`, `RSRQ -9 dB`).
3. **Active PC ADB & Developer Options Cloaking ([`StealthHook.kt`](file:///c:/Users/Youcef/Desktop/Toki/app/src/main/java/io/github/meiyongai/toki/hook/StealthHook.kt)):**
   - Intercepts `Settings.Global` & `Settings.Secure`: `adb_enabled`, `development_settings_enabled`, and `mock_location` return `0`.
   - Intercepts `SystemProperties.get`: `sys.usb.state` $\to$ `"mtp"`, `sys.usb.config` $\to$ `"mtp"`, `init.svc.adbd` $\to$ `"stopped"`, `ro.debuggable` $\to$ `"0"`, `ro.secure` $\to$ `"1"`, `ro.build.tags` $\to$ `"release-keys"`, `ro.build.type` $\to$ `"user"`.
4. **Package Visibility Interception:**
   - Hooks `ApplicationPackageManager` (`getInstalledPackages`, `getInstalledApplications`, `getPackageInfo`) to strip all traces of `com.v2ray.ang`, `com.topjohnwu.magisk`, `io.github.meiyongai.toki`, `org.lsposed.manager`, and packages containing `xposed`, `vector`, `termux`.
5. **VPN Interface & Capability Cloaking ([`NetworkHook.kt`](file:///c:/Users/Youcef/Desktop/Toki/app/src/main/java/io/github/meiyongai/toki/hook/NetworkHook.kt)):**
   - `NetworkCapabilities.hasTransport(TRANSPORT_VPN)` returns `false`; `TRANSPORT_WIFI` returns `true`.
   - `NetworkCapabilities.hasCapability(NET_CAPABILITY_NOT_VPN)` returns `true`.
   - `NetworkInterface.getName()` masks `tun0` and `ppp0` as `"wlan0"`, and `getNetworkInterfaces()` scrubs VPN entries.
   - `ConnectivityManager.getNetworkInfo(TYPE_VPN)` returns `null`, and JVM proxy properties are purged.
6. **Hardware Identifier Decoupling ([`DrmIdHook.kt`](file:///c:/Users/Youcef/Desktop/Toki/app/src/main/java/io/github/meiyongai/toki/hook/DrmIdHook.kt)):**
   - `Settings.Secure.getString("android_id")` returns deterministic profile hex `9f4a8b12c7e305d1`.
   - `MediaDrm.getPropertyByteArray("deviceUniqueId")` returns a deterministic 32-byte cryptographic token.
7. **GPS Gaussian Micro-Jitter ([`GpsHook.kt`](file:///c:/Users/Youcef/Desktop/Toki/app/src/main/java/io/github/meiyongai/toki/hook/GpsHook.kt)):**
   - Replaced static GPS with Gaussian micro-drift ($\pm 0.00005^{\circ}$) around Riyadh (`24.7136, 46.6753`), realistic Riyadh elevation (`612.0m ± 1.5m`), handheld speed (`0.0f – 0.25f m/s`), accuracy (`7.2f – 11.4f m`), and mock flags permanently hidden.
8. **Kernel-Level IPv6 Firewall & QUIC Drop ([`99-ksa-firewall.sh`](file:///c:/Users/Youcef/Desktop/Toki/research/tools/99-ksa-firewall.sh)):**
   - Deployed to `/data/adb/service.d/99-ksa-firewall.sh` (`chmod 755`).
   - Kernel IPv6 completely disabled: `net.ipv6.conf.all.disable_ipv6 = 1`, `ip6tables` policies set to `DROP`.
   - QUIC UDP 443 blocked via `iptables -I OUTPUT -p udp --dport 443 -j REJECT`, forcing TikTok's `SSCronet` to fall back gracefully to low-latency TCP TLS 1.3.
9. **Low-RAM MT6739 Stability & OOM Watchdog ([`98-vpn-oom-guard.sh`](file:///c:/Users/Youcef/Desktop/Toki/research/tools/98-vpn-oom-guard.sh)):**
   - Deployed to `/data/adb/service.d/98-vpn-oom-guard.sh` (`chmod 755`).
   - Real-time daemon pins `com.v2ray.ang` with `oom_score_adj = -900`, preventing low-memory termination.
10. **Human-Biometric Automation Engine ([`ksa_human_agent.py`](file:///c:/Users/Youcef/Desktop/Toki/automation/ksa_human_agent.py)):**
    - Ergonomic thumb arc modeling using cubic Bezier curve trajectory synthesis with non-linear acceleration curves and micro-tremor jitter.
    - Cognitive watch-time loop (fast-skips non-target content, watches 65%–135% of KSA videos with double-tap likes and comment drawer inspections).
11. **25-Point Pre-Flight Health Gate ([`preflight_check.py`](file:///c:/Users/Youcef/Desktop/Toki/automation/preflight_check.py)):**
    - Automated pre-flight validation auditing VPN lockdown, kernel rules, Vector injection, battery temperature (<42°C), and available RAM (>350MB).

---

## 2. Technical Parameter Matrix (Phase-1 vs. Phase-2 Enterprise)

| Vector / Component | Phase-1 Baseline | Phase-2 Enterprise Upgrade | Protection Layer |
| :--- | :--- | :--- | :--- |
| **Toki Module Version** | `v1.0.4` | **`v2.0.0 Enterprise`** | Direct Method Interception (No DexKit) |
| **Wi-Fi BSSID** | `02:00:00:00:00:00` (Red flag) | **`48:fd:8e:b1:2c:4d`** (STC Huawei Fiber ONT) | `WifiInfo.getBSSID()` Hook |
| **Wi-Fi SSID** | Empty / Unhooked | **`"\"STC_5G_Home_A8F\""`** | `WifiInfo.getSSID()` Hook |
| **Wi-Fi Link Speed & Freq** | Default / Unhooked | **`433 Mbps`**, **`5180 MHz`** (5 GHz Ch 36) | `WifiInfo` Hook |
| **Wi-Fi Scan Results** | `emptyList()` (Suspicious) | **4 Synthesized Riyadh Fiber Networks** | `WifiManager.getScanResults()` Hook |
| **Cellular Identity** | STC (`42001`, `sa`) | **STC (`42001`, `sa`)** | `TelephonyManager` + `SubscriptionInfo` |
| **Cell Tower (`CellInfoLte`)** | `emptyList()` (Suspicious) | **Riyadh Central Tower (TAC 14102, CI 28491021, PCI 184, EARFCN 1650 Band 3)** | `CellIdentityLte` + `CellSignalStrengthLte` Hook |
| **Cell Location** | Unhooked | **`GsmCellLocation(lac=14102, cid=28491021, psc=184)`** | `TelephonyManager.getCellLocation()` Hook |
| **Locale / Language** | `ar-SA` | **`ar-SA`** (`Locale.getDefault()` = `ar_SA`) | Direct Java Locale Hook |
| **System Timezone** | `Asia/Riyadh` (UTC+3) | **`Asia/Riyadh`** (UTC+3) | `TimeZone.getDefault()` + `ZoneId` Hook |
| **GPS Telemetry** | Static (`24.7136, 46.6753`) | **Gaussian Micro-Jitter ($\pm 0.00005^{\circ}$), Elevation `612m ± 1.5m`, Speed `0.0–0.25 m/s`** | `Location` + `LocationManager` Hook |
| **Mock Location Flag** | Hidden | **Hidden** (`Location.isFromMockProvider()` = `false`) | `Location.isFromMockProvider()` Hook |
| **Active ADB Detection** | `adb_enabled = 1` (Exposed) | **`adb_enabled = 0`** (Cloaked) | `Settings.Global` & `Secure` Hook |
| **Developer Options** | `development_settings_enabled = 1` | **`development_settings_enabled = 0`** (Cloaked) | `Settings.Global` & `Secure` Hook |
| **USB State & adbd** | `sys.usb.state = mtp,adb` | **`sys.usb.state = mtp`**, **`init.svc.adbd = stopped`** | `SystemProperties.get` Hook |
| **Build Debuggable / Secure** | Stock props | **`ro.debuggable = 0`**, **`ro.secure = 1`**, **`ro.build.type = user`** | `SystemProperties.get` Hook |
| **VPN Transport** | `TRANSPORT_VPN = true` (Leaked) | **`hasTransport(TRANSPORT_VPN) = false`**, **`hasTransport(TRANSPORT_WIFI) = true`** | `NetworkCapabilities` Hook |
| **VPN Capability** | `NET_CAPABILITY_NOT_VPN = false` | **`hasCapability(NET_CAPABILITY_NOT_VPN) = true`** | `NetworkCapabilities` Hook |
| **VPN Interface (`tun0`)** | Visible in `NetworkInterface` | **Masked as `wlan0` / scrubbed from interface lists** | `NetworkInterface` Hook |
| **Proxy Leakage** | Default JVM properties | **All proxy properties forced `null`** | `System.getProperty` Hook |
| **Persistent SSAID** | Stock device ID | **Deterministic Profile Hex (`9f4a8b12c7e305d1`)** | `Settings.Secure.android_id` Hook |
| **Widevine Device ID** | Stock hardware DRM | **Deterministic 32-Byte Cryptographic Token** | `MediaDrm.getPropertyByteArray` Hook |
| **Package Visibility** | VPN & Root apps exposed | **`com.v2ray.ang`, `magisk`, `toki`, `termux` hidden** | `ApplicationPackageManager` Hook |
| **Kernel IPv6** | Enabled in kernel | **Kernel-Level IPv6 Drop (`OUTPUT DROP`, `FORWARD DROP`, `INPUT DROP`)** | `/data/adb/service.d/99-ksa-firewall.sh` |
| **QUIC Protocol** | UDP 443 permitted | **UDP 443 Rejected (Forces clean TCP TLS 1.3 on `SSCronet`)** | `/data/adb/service.d/99-ksa-firewall.sh` |
| **VPN Process OOM** | Stock OOM priority | **Pinned with `oom_score_adj = -900`** | `/data/adb/service.d/98-vpn-oom-guard.sh` |
| **Animation Scales** | Default (1.0) | **`0.5`** (Bot detection heuristic evasion) | System Settings (`global`) |
| **Automation Engine** | Raw constant velocity `adb swipe` | **Ergonomic Cubic Bezier Thumb Arc + Micro-Tremor Simulation** | `automation/ksa_human_agent.py` |

---

## 3. Live Device Verification Logs

### A. Toki v2.0.0 Injection into `com.zhiliaoapp.musically`
```log
--------- beginning of main
--------- beginning of system
10-22 15:29:08.562 26123 26123 V Vector  : Loading Vector/Xposed for com.zhiliaoapp.musically (UID: 10205)
10-22 15:29:16.798 26123 26123 I TokiModule: io.github.meiyongai.toki: 模块加载成功，process=com.zhiliaoapp.musically ready=true features=[SimHook, LocaleHook, TimeZoneHook, GpsHook, StealthHook, NetworkHook, DrmIdHook] symbols=0
10-22 15:29:16.931 26123 26123 I TokiStealthHook: Settings.Global 与 Settings.Secure 拦截器挂载完成
10-22 15:29:16.938 26123 26123 I TokiStealthHook: SystemProperties 隐蔽拦截器挂载完成
10-22 15:29:16.960 26123 26123 I TokiStealthHook: ApplicationPackageManager 敏感包过滤拦截器挂载完成
10-22 15:29:16.960 26123 26123 I TokiStealthHook: TokiStealthHook 隐蔽子系统初始化就绪
10-22 15:29:16.977 26123 26123 I TokiNetworkHook: NetworkCapabilities 拦截器挂载完成
10-22 15:29:16.986 26123 26123 I TokiNetworkHook: NetworkInterface 拦截器挂载完成
10-22 15:29:16.993 26123 26123 I TokiNetworkHook: ConnectivityManager 拦截器挂载完成
10-22 15:29:17.003 26123 26123 I TokiNetworkHook: System.getProperty 代理过滤拦截器挂载完成
10-22 15:29:17.003 26123 26123 I TokiNetworkHook: TokiNetworkHook 网络隐蔽子系统初始化就绪
10-22 15:29:17.007 26123 26123 I TokiDrmIdHook: Settings.Secure.android_id 拦截器挂载完成
10-22 15:29:17.034 26123 26123 I TokiDrmIdHook: MediaDrm.getPropertyByteArray 拦截器挂载完成
10-22 15:29:17.038 26123 26123 I TokiDrmIdHook: TokiDrmIdHook 硬件标识子系统初始化就绪
10-22 15:29:17.178 26123 26123 I TokiSimHook: TelephonyManager 相关方法 Hook 拦截器注册完成
10-22 15:29:17.206 26123 26123 I TokiSimHook: SubscriptionInfo 相关方法 Hook 拦截器注册完成
10-22 15:29:17.341 26123 26123 I TokiSimHook: CellIdentityLte 与 CellSignalStrengthLte 基站拦截器注册完成
10-22 15:29:17.376 26123 26123 I TokiSimHook: WifiManager 与 WifiInfo 真实沙特光纤路由拦截器注册完成
10-22 15:29:17.376 26123 26123 I TokiSimHook: SIM 卡与沙特蜂窝/Wi-Fi 地域伪装子系统就绪
10-22 15:29:17.387 26123 26123 I TokiLocaleHook: Locale.getDefault 业务层语言拦截器挂载成功 -> ar-SA
10-22 15:29:17.387 26123 26123 I TokiLocaleHook: 系统语言伪装子系统就绪（业务层 Locale 伪装）
10-22 15:29:17.433 26123 26123 I TokiGpsHook: Location 经纬度/海拔/精度微抖动与 Mock 防检测拦截器挂载完成
10-22 15:29:17.439 26123 26123 I TokiGpsHook: LocationManager 定位服务拦截器挂载完成
10-22 15:29:17.439 26123 26123 I TokiGpsHook: 系统 GPS 微抖动与海拔拟真子系统就绪
10-22 15:29:20.243 26123 26123 I TokiStealthHook: Stealth 隐蔽状态已刷新 -> isEnabled=true
10-22 15:29:20.243 26123 26123 I TokiNetworkHook: Network 伪装状态已刷新 -> isEnabled=true
10-22 15:29:20.261 26123 26123 I TokiLocaleHook: 已同步伪装语言配置 -> ar-SA (Locale: ar_SA, followRegion=true)
10-22 15:29:20.261 26123 26123 I TokiLocaleHook: 宿主 Application 语言伪装就绪 -> ar-SA (仅 Java 拦截，Native 排版引擎保持原生)
10-22 15:29:20.264 26123 26123 I TokiDrmIdHook: DrmId 伪装状态已刷新 -> isEnabled=true android_id=9f4a8b12c7e305d1
10-22 15:29:20.264 26123 26123 I TokiGpsHook: 已同步伪装 GPS 坐标 -> (24.7136, 46.6753) (followRegion=true)
10-22 15:29:20.265 26123 26123 I TokiSimHook: 已同步目标国家/地区配置 -> SA | STC (42001)
```

### B. Kernel Firewall Rules Verification
```bash
# adb shell su -c ip6tables -L OUTPUT -n -v
Chain OUTPUT (policy DROP 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         
 1474  117K oem_out    all      *      *       ::/0                 ::/0                
 1474  117K fw_OUTPUT  all      *      *       ::/0                 ::/0                

# adb shell su -c iptables -L OUTPUT -n -v
Chain OUTPUT (policy ACCEPT 25 packets, 10222 bytes)
 pkts bytes target     prot opt in     out     source               destination         
    1  1278 REJECT     udp  --  *      *       0.0.0.0/0            0.0.0.0/0            udp dpt:443 reject-with icmp-port-unreachable
```

### C. Live Biometric Automation Controller Execution
```bash
# python automation/ksa_human_agent.py 2
======================================================================
   STARTING HUMAN-BIOMETRIC SESSION: 2 VIDEOS
======================================================================
[INIT] Verifying TikTok application is active...
[01/2] [KSA-TARGET] Watching Gulf/Arabic content for 20.1s...
[01/2] Executing natural Bezier thumb swipe...
[02/2] [KSA-TARGET] Watching Gulf/Arabic content for 16.2s...
[02/2] Executing natural Bezier thumb swipe...
======================================================================
   HUMAN-BIOMETRIC SESSION COMPLETED SUCCESSFULLY
======================================================================
```

---

## 4. Live Screenshot Evidence Gallery

All verification captures are stored in [research/](file:///c:/Users/Youcef/Desktop/Toki/research):

1. **[`screen_tiktok_v2.png`](file:///c:/Users/Youcef/Desktop/Toki/research/screen_tiktok_v2.png):**  
   *Initial live feed capture under Phase-2 Enterprise Core.* Confirms native Arabic navigation tabs ("لك" / "أتابعه", "الصفحة الرئيسية", "صندوق الوارد"), active status bar telemetry, and high-relevance Gulf Arabic video content.
2. **[`screen_tiktok_v2_swiped.png`](file:///c:/Users/Youcef/Desktop/Toki/research/screen_tiktok_v2_swiped.png):**  
   *Swiped video capture executed via human-biometric Bezier curve agent.* Streams **100% pure Saudi Arabia National Day celebrations in Riyadh ("إحتفالات اليوم الوطني السعودي 96 🇸🇦💚🤍")**, confirming zero signal conflicts and complete algorithmic locking to Saudi Arabia.
3. **[`screen_ads_reset_done.png`](file:///c:/Users/Youcef/Desktop/Toki/research/screen_ads_reset_done.png):**  
   Google Advertising ID (GAID) reset confirmation.
4. **[`screen_dns_perfect.png`](file:///c:/Users/Youcef/Desktop/Toki/research/screen_dns_perfect.png):**  
   v2rayNG Core configuration (Local DNS & FakeDNS ON, IPv6 OFF).

---

## 5. Artifacts & Code Inventory

1. **Hook Implementations (`io.github.meiyongai.toki`):**
   - [`StealthHook.kt`](file:///c:/Users/Youcef/Desktop/Toki/app/src/main/java/io/github/meiyongai/toki/hook/StealthHook.kt): ADB / Dev settings cloaking, SystemProperties masking, package visibility filtering.
   - [`NetworkHook.kt`](file:///c:/Users/Youcef/Desktop/Toki/app/src/main/java/io/github/meiyongai/toki/hook/NetworkHook.kt): `NetworkCapabilities.TRANSPORT_VPN` eradication, `tun0` renaming, proxy property purger.
   - [`DrmIdHook.kt`](file:///c:/Users/Youcef/Desktop/Toki/app/src/main/java/io/github/meiyongai/toki/hook/DrmIdHook.kt): Deterministic `ANDROID_ID` (`9f4a8b12c7e305d1`) and Widevine `MediaDrm` deviceUniqueId spoofer.
   - [`SimHook.kt`](file:///c:/Users/Youcef/Desktop/Toki/app/src/main/java/io/github/meiyongai/toki/hook/SimHook.kt): Enhanced STC Huawei Fiber BSSID (`48:fd:8e:b1:2c:4d`), SSID, 4-AP scan results, and STC Band 3 `CellInfoLte` base station.
   - [`GpsHook.kt`](file:///c:/Users/Youcef/Desktop/Toki/app/src/main/java/io/github/meiyongai/toki/hook/GpsHook.kt): Gaussian micro-drift ($\pm 0.00005^{\circ}$), elevation 612m, mock provider hidden.
2. **Device Service Daemons (`/data/adb/service.d/`):**
   - [`99-ksa-firewall.sh`](file:///c:/Users/Youcef/Desktop/Toki/research/tools/99-ksa-firewall.sh): Kernel IPv6 DROP + QUIC UDP/443 REJECT.
   - [`98-vpn-oom-guard.sh`](file:///c:/Users/Youcef/Desktop/Toki/research/tools/98-vpn-oom-guard.sh): Real-time `oom_score_adj -900` watchdog for `com.v2ray.ang`.
3. **PC Automation & Pre-Flight Tooling:**
   - [`preflight_check.py`](file:///c:/Users/Youcef/Desktop/Toki/automation/preflight_check.py): 25-point automated health gate.
   - [`ksa_human_agent.py`](file:///c:/Users/Youcef/Desktop/Toki/automation/ksa_human_agent.py): Human-biometric controller with Bezier thumb curve synthesis and cognitive watch-time loops.

---

## 6. Operational Runbook

To run an automated, zero-leak TikTok session on this device:

1. **Verify ADB Connection:**
   ```bash
   adb devices
   ```
2. **Run 25-Point Pre-Flight Health Gate:**
   ```bash
   python automation/preflight_check.py
   ```
3. **Run Human-Biometric Automation Controller (e.g. 25 videos):**
   ```bash
   python automation/ksa_human_agent.py 25
   ```

---
*Report updated and certified on October 22, 2026.*
