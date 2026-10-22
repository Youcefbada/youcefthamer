# 🔬 Deep-Dive Architectural Analysis: ByteDance Client Telemetry, Native Attestation & Linux Netfilter Invariance

**Document ID:** `TOKI-RESEARCH-BYTEDANCE-TELEMETRY-DEEPDIVE-001`  
**Classification:** Enterprise Engineering Reference & Threat Model  
**Target Platform:** Android 11 (API 30), MediaTek MT6739, ARMv7-A (32-bit userspace)  
**Target Engine:** ByteDance MSSDK / MetaSec (`libmetasec_ml.so`), `libmsaoaidsec.so`, `libttboringssl.so`, `SSCronet`

---

## AREA 1: Device Registration & Cryptographic Token Architecture

In ByteDance's client architecture (historically designated as the Applog / MSSDK / MetaSec subsystem), device identity and request signing are bifurcated into:
1. **Identity Provisioning Phase:** `/service/2/device_register/`
2. **Per-Request Cryptographic Attestation Phase:** `X-Gorgon`, `X-Khronos`, `X-Ladon`, `X-Argus`

### 1. The `/service/2/device_register/` Pipeline
When the application initializes, the native Applog library aggregates a hardware, environment, and storage snapshot, compresses it (gzip/lz4), and encrypts the payload via custom white-box AES / `ttEncrypt` routines inside `libEncryptor.so` / `libmetasec_ml.so` before POSTing to the registration endpoint.

The backend uses this telemetry to issue a new `device_id` (`did`) and `install_id` (`iid`) or bind the device to an existing hardware cluster in ByteDance’s device-graph:

```
[Client Environment] 
   ├─ Hardware Identifiers (MediaDrm 32-byte UUID, ANDROID_ID, Build.SERIAL)
   ├─ SoC & Kernel Metrics (MemTotal exact bytes, CPU part/clusters, /data partition block count)
   ├─ Sensor HAL Profile (Sensor names, vendors, resolutions, max ranges)
   └─ FS Timestamps (boot_id, statx birth times of build.prop & /data/system)
           │
           ▼ (Native Encryption: libEncryptor.so / libmetasec_ml.so)
   POST /service/2/device_register/
           │
           ▼
[ByteDance Risk Backend Engine]
   ├─ Graph Match: Matches fuzzy-hash against existing hardware records
   └─ Resolution:
        ├─ New Hardware Node ──► Issues Fresh `did` & `iid`
        └─ Known Hardware Node ─► Re-links to Historical `did` Cluster
```

#### Persistent & Semi-Persistent Identifiers
- **`openudid` / `clientudid`:** Client-generated UUIDs cached in app-private storage, SharedPreferences (`applog_stats`), and hidden fallback locations.
- **`Build.SERIAL` & `ANDROID_ID` (`Settings.Secure.ANDROID_ID`):** Scoped per-signing-key and per-user on Android 8.0+.
- **Widevine `MediaDrm` ID:** The 32-byte deterministic hardware identifier queried from the Widevine Trusted Application (TA) via `getPropertyByteArray("deviceUniqueId")`.
- **`drm_id` / `oaid` (`libmsaoaidsec.so`):** Mobile Security Alliance hardware identifier where applicable.

#### Immutable Hardware Geometry & SoC Signatures
- **`/proc/cpuinfo` & `/sys/devices/system/cpu/`:** CPU implementer, part, revision, cluster topology, and exact frequency step tables.
- **`/proc/meminfo` & `StatFs`:** Exact total kernel-accessible physical RAM bytes (`MemTotal`—which varies slightly by kernel build and reserved modem/framebuffer carveouts) and exact block count (`f_blocks`) of the `/data` partition.
- **Sensor Hardware Metadata:** Exact strings returned by `Sensor.getName()`, `Sensor.getVendor()`, `Sensor.getVersion()`, `Sensor.getResolution()`, and `Sensor.getMaximumRange()` for every sensor registered in the HAL.
- **Boot & File System Timestamps:** `/proc/sys/kernel/random/boot_id`, `statx` birth/modification times (`st_ctime`, `st_mtime`) of `/system/build.prop`, `/data/system`, and the APK installation directory (`/data/app/~~[randomHash]/com.zhiliaoapp.musically-[randomHash]/`).

#### Server-Side Graph Resolution (`did` vs. `iid`)
- **`iid` (Install ID):** Represents an installation instance. Clearing application data or reinstalling generates a new `iid`.
- **`did` (Device ID):** Represents the physical hardware entity. If an installation sends a fresh `clientudid` and a new `ANDROID_ID`, yet the combination of MediaDrm ID, `/data` partition block count, sensor descriptor list, and network BSSID/IP matches a previously seen hardware node with high fuzzy-hash similarity, the backend returns the existing `did` (or silently links the new `did` to the historical hardware cluster in the risk graph).

---

### 2. Cryptographic Request Signing Headers

Every subsequent API call is cryptographically signed by `libmetasec_ml.so` to prove that the request originated from an unmodified client running in an untampered environment:

| Header | Role & Cryptographic Structure |
| :--- | :--- |
| **`X-Khronos`** | Unix epoch timestamp (seconds) when the signature was generated. Acts as a freshness nonce against replay attacks. |
| **`X-Gorgon`** | Legacy/baseline MAC signature (typically prefix `0404...` or `8404...`). Computes a keyed hash over URL query string, `X-SS-STUB` (MD5 of HTTP POST body), `Cookie` header (`sessionid`, `tt_webid`), and `X-Khronos`. |
| **`X-Ladon`** | Encrypted timestamp and environment seed validation token (Base64-encoded ciphertext generated from a key derived from `aid` and `lc_id`). |
| **`X-Argus`** | The primary anti-bot and environment-attestation protobuf payload. Encrypts a serialized Protobuf structure using multi-round custom block encryption (AES-CBC, custom S-boxes, and SM3/SHA-256 key derivation inside a virtualized OLLVM VM). |

#### What Lives Inside `X-Argus`:
Unlike `X-Gorgon` (which primarily validates HTTP transport integrity), `X-Argus` embeds client-side risk flags and runtime telemetry directly inside the encrypted Protobuf fields:
- **Action Counters:** Number of touch events vs. number of network requests since process launch.
- **Environment Integrity Bitmasks:** Flags indicating whether `libmetasec_ml.so` detected unexpected memory maps in `/proc/self/maps`, presence of seccomp signal handlers, debugger attachment `TracerPid`, or discrepancies between Java `SystemProperties` and native `__system_property_find`.
- **Identity Digest:** Digest of current `did`, `iid`, `app_version`, and `os_version`.
- **Silent Fail Behavior:** An anomaly detected by `libmetasec_ml.so` does not crash the client locally; instead, the client sets an anomaly flag inside `X-Argus`. The backend silently drops the action (likes/follows do not persist, or account registration triggers an unsolvable slider CAPTCHA or "Too many attempts" error).

---

## AREA 2: Play Integrity API & Hardware Keystore Attestation

### 1. Play Integrity Enforcement Tiers
Google's Play Integrity API provides three primary device attestation verdicts inside its signed, encrypted JSON Web Token (JWS):
- **`MEETS_BASIC_INTEGRITY`:** Passes if the device runs a recognizable Android build without obvious uncloaked root indicators in userspace.
- **`MEETS_DEVICE_INTEGRITY`:** Requires that the app is running on a certified Android device powered by Google Play Services that passes system integrity checks. On Android 13+, Google increasingly requires hardware-backed signals for `MEETS_DEVICE_INTEGRITY`, whereas on older devices (or via legacy fallback logic), software-evaluated system state could suffice.
- **`MEETS_STRONG_INTEGRITY`:** Strictly requires hardware-backed proof of boot integrity (`verifiedBootState == Verified` and `deviceLocked == true`) signed by a hardware Keymaster implementation inside a Trusted Execution Environment (TEE) or StrongBox, alongside a recent security patch level.

#### Platform Composite Risk Scoring
Because millions of legitimate users in developing markets use budget devices with broken OEM Keymaster implementations, outdated security patches, or custom ROMs, enforcing `MEETS_STRONG_INTEGRITY` globally would block a large portion of real human users. Consequently, platforms use composite risk scoring:
- **High-Friction Endpoints:** Account creation, SMS/Email binding, password resets, creator monetization, and TikTok Shop checkout trigger asynchronous Play Integrity token requests (`StandardIntegrityManager` or `IntegrityManager.requestIntegrityToken`).
- **Risk Weighting:** A missing `MEETS_STRONG_INTEGRITY` verdict alone rarely causes an outright ban if `MEETS_DEVICE_INTEGRITY` is present and network/behavioral telemetry is clean. However, failing `MEETS_DEVICE_INTEGRITY` (returning only `MEETS_BASIC_INTEGRITY` or an empty verdict) drastically lowers the account trust ceiling, forcing immediate CAPTCHA challenges or restricting outbound social actions.

### 2. Keymaster & TEE Mechanics on MediaTek MT6739 (`SM-A022F`)
On the Samsung Galaxy A02 (`SM-A022F`, Android 11), the hardware cryptographic pipeline operates as follows:
1. When an app (or Google Play Services `com.google.android.gms.unstable`) requests hardware key attestation via `KeyPairGenerator.getInstance("EC", "AndroidKeyStore")` with `.setAttestationChallenge(nonce)`, the call crosses IPC Binder to `/system/bin/keystore`.
2. `keystore` invokes the vendor HAL service (`android.hardware.keymaster@3.0-service` or `@4.0-service` backed by Microtrust `teei_daemon` communicating with `/dev/teei_client` or Trustonic `mcDriverDaemon`).
3. The TEE reads the physical hardware fuses and boot parameters passed by the Little Kernel (`lk`) bootloader at boot time (`unlocked` state) before Android ever starts. Modifying `ro.boot.verifiedbootstate` via `resetprop -n` alters the userspace `/dev/__properties__` tmpfs region in Linux RAM, but cannot alter the state held inside the isolated TrustZone secure world.
4. The TEE signs the X.509 leaf certificate containing `deviceLocked = FALSE` and `verifiedBootState = UNVERIFIED` using the device-specific key chained to the OEM/Google Hardware Attestation Root.

---

## AREA 3: Inertial-Sensor Dynamic Coupling (Biomechanical Analysis)

### 1. How Behavioral ML Evaluates Touch-Inertial Cross-Correlation
In mobile fraud detection, sensor fusion models analyze whether touch inputs are physically possible given the device's inertial state.
- **Data Collection Window:** `libmetasec_ml.so` registers a `SensorEventListener` (or native `ASensorEventQueue` via `libandroid.so`) at `SENSOR_DELAY_GAME` (20 ms / 50 Hz) or `SENSOR_DELAY_UI` (60 ms / 16.6 Hz).
- **Feature Extraction:** For every touch gesture (`ACTION_DOWN` at $t_{\text{down}}$ to `ACTION_UP` at $t_{\text{up}}$), the engine extracts a time-series window $[t_{\text{down}} - 100\text{ ms}, t_{\text{up}} + 200\text{ ms}]$ from the accelerometer buffer:
  - **Zero-Variance / Flatline Detection:** Calculates the rolling standard deviation $\sigma_a = \sqrt{\sigma_x^2 + \sigma_y^2 + \sigma_z^2}$. On a real MEMS accelerometer, thermal and electronic ADC noise produces a non-zero baseline variance across the least-significant bits. Furthermore, a stationary table orientation yields $X \approx 0, Y \approx 0, Z \approx 9.81\text{ m/s}^2$, which is ergonomics-incompatible with continuous vertical video consumption.
  - **Impulse Cross-Correlation ($R_{FM}$):** Computes the cross-correlation between the touch pressure/velocity profile $F(t)$ and the high-pass filtered magnitude of linear acceleration $a_{\text{lin}}(t) = \Vert{}\vec{a}(t) - \vec{g}(t)\Vert{}$:
    $$R(\tau) = \int F(t) \cdot a_{\text{lin}}(t + \tau) \, dt$$
    In genuine handheld operation, $R(\tau)$ exhibits a statistically significant peak at lag $\tau \in [10\text{ ms}, 40\text{ ms}]$. If $R(\tau) \approx 0$ across 50 consecutive swipes, the session is classified as an automated stationary rig.

### 2. Linux Input Subsystem vs. Android Sensor HAL on SM-A022F
The Galaxy A02 uses the MediaTek Sensor Manager (`hwmsen`) architecture:
- If the vendor's `sensors.mt6739.so` HAL reads from `/dev/input/event9`, writing `EV_ABS` (`ABS_X`, `ABS_Y`, `ABS_Z`) + `EV_SYN` (`SYN_REPORT`) events directly to `/dev/input/event9` has a major side effect: the real hardware MEMS chip is still polling and writing its own `ABS_X/Y/Z` events to `/dev/input/event9` every 20ms.
- If a background process writes synthetic values to `/dev/input/event9` while the kernel I2C driver continues emitting flat table values ($X=0, Y=0, Z=9810$), the resulting sensor stream seen by the app will oscillate wildly between the table orientation ($0, 0, 9.81$) and the synthetic tilted orientation, creating an impossible square-wave acceleration spike of $> 5\text{ m/s}^2$ at 50 Hz.
- **Architectural Solution:** Hardware polling is controlled via `/sys/class/sensor/m_acc_misc/accactive` (or `/sys/class/input/input9/enable`), or intercepted within the `SensorEventQueue` dispatcher so hardware and synthetic streams do not collide.

---

## AREA 4: Zero-Interface Transparent Proxy (Linux Netfilter Architecture)

To route TCP and DNS traffic through a local proxy core (`xray` or `sing-box`) without creating a `tun0` or `ppp0` virtual network interface (which would be visible to raw `AF_NETLINK` `RTM_GETLINK` socket dumps), Linux Netfilter provides two interface-less mechanisms for locally generated (`OUTPUT` chain) traffic:

### NAT REDIRECT vs. Mangle TPROXY
- **NAT REDIRECT (`iptables -t nat -A OUTPUT`):** Rewrites destination IP to `127.0.0.1` and destination port to the local proxy's `dokodemo-door` listening port. The proxy reads original destination IP/port via the `SO_ORIGINAL_DST` socket option.
  - *Advantage:* Extremely fast, requires zero virtual network interfaces (`ip link` shows only `lo`, `wlan0`, and cellular `ccmni*`), and requires no mangle routing loopbacks for TCP.
- **Mangle TPROXY via Loopback (`ip rule` + `iptables -t mangle`):** Required only if multi-port UDP proxying is needed. Since all non-DNS outbound UDP for the target UID is dropped to prevent WebRTC/QUIC leaks, NAT REDIRECT is cleaner, lower-overhead on MT6739, and completely eliminates `tun0`.

### Complete Zero-Interface Architecture

```
[Target App: com.zhiliaoapp.musically (UID 10205)]
       │
       ├─► DNS Query (UDP/TCP 53) ──► iptables REDIRECT ──► 127.0.0.1:10853 (Xray DNS)
       ├─► HTTP/HTTPS (TCP 80/443) ─► iptables REDIRECT ──► 127.0.0.1:10810 (Xray dokodemo-door)
       ├─► QUIC (UDP 443) ──────────► iptables REJECT ────► Immediate ICMP Port Unreachable
       └─► Direct UDP on wlan0 ─────► iptables REJECT ────► Immediate ICMP Net Unreachable
                                                                  │
                                                        [Physical wlan0]
                                                  (Zero tun0 / Zero ppp0 exist)
```

---

## AREA 5: Behavioral Telemetry & Statistical Anomaly Models

ByteDance’s behavioral risk models evaluate the following telemetry dimensions to separate human sessions from automation scripts:

### 1. Dwell Time Distributions (Lognormal vs. Uniform)
- **The "Skip" Mode ($t < 2.2\text{ s}$):** Users evaluate the visual hook within the first 800 to 2200 ms. If uninterested, they swipe immediately.
- **The "Engaged" Mode ($t \ge 0.8 \cdot D_{\text{video}}$):** If a user passes the 3-second threshold, probability of watching until near the end of video duration $D_{\text{video}}$ (or looping $1.1\times$ to $1.8\times$ on short 7–15 second clips) rises sharply.
- **The Uncanny Valley:** An automated script that watches every video for a randomized 12 to 32 seconds regardless of whether the video is 6 seconds long (resulting in an arbitrary partial loop) or 60 seconds long (abandoning mid-sentence) exhibits zero correlation. Risk engines compute the ratio:
  $$r = \frac{T_{\text{dwell}}}{D_{\text{video}}}$$
  Organic sessions cluster around $r \in [0.05, 0.20]$ (fast skips) and $r \in [0.95, 1.40]$ (completions/loops).

### 2. Fling Kinematics & Spatial Heatmap Entropy
- **Fling Kinematics:** When a human swipes up on Android's `ViewPager2`, `VelocityTracker` calculates the initial release velocity $v_0$ in pixels per second.
- **Spatial Heatmap Entropy:** Over a 20-minute session, humans shift grip positions (from one-handed right thumb to two-handed index finger, or shifting the thumb pivot point lower on the bezel). Automated drivers that calculate cubic Bézier curves from a static bounding box get flagged by Spatial Heatmap Entropy detectors, which construct a 2D kernel density estimation (KDE) of `ACTION_DOWN` and `ACTION_UP` coordinates over 500+ swipes.

### 3. Environmental & UI Micro-Signals
- **Audio State Telemetry:** `AudioManager.getStreamVolume(STREAM_MUSIC)` and headphone state. Devices watching hundreds of videos with volume permanently at 0 or a static integer without volume-key presses (`KEYCODE_VOLUME_UP`/`DOWN`) deviate from organic cohorts.
- **Battery & Thermal Discrepancies:** `/sys/class/power_supply/battery/status`, `capacity`, `voltage_now`, `temp`. Phones mounted in continuous automation racks typically remain plugged into USB power 24/7 (status = Full, capacity = 100%, plugged = USB/AC). Risk models penalize accounts whose entire lifecycle occurs while `BatteryManager.EXTRA_PLUGGED > 0` at 100% charge with zero discharge cycles.
- **UI Navigation Graph Entropy:** Organic sessions are non-linear—users occasionally pause a video (single tap), inspect comments (`comment_list_show`), scroll comments without typing, tap creator avatars, press the back button, or background the app (`onPause` $\to$ `onStop`) in the middle of a video.
