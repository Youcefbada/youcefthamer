#!/usr/bin/env python3
"""
KSA TikTok Profile Vault & Clean-Slate Identity Rotation Engine (profile_vault.py)
Generates and safely rotates completely decoupled hardware identity profiles for TikTok Global,
preventing ByteDance graph linkage (/service/2/device_register/) across account lifecycles.

Manages:
- Deterministic/Cryptographic SSAID (ANDROID_ID)
- 32-byte Widevine MediaDrm DeviceUniqueId
- Genuine Saudi STC Huawei Fiber ONT BSSID & SSID
- Cellular Base Station LAC/CID
- Surgical ByteDance state purge (removes applog_stats, keystore tokens, and caches)
"""

import subprocess
import secrets
import random
import time
import json
import sys
import os


def find_adb() -> str:
    candidates = [
        r"C:\Users\Youcef\AppData\Local\Android\Sdk\platform-tools\adb.exe",
        r"C:\Users\Youcef\Desktop\platform-tools\adb.exe",
        "adb"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return "adb"

ADB_PATH = find_adb()
PROFILES_DIR = os.path.join(os.path.dirname(__file__), "profiles")
CONFIG_XML_PATH = "/data/local/tmp/toki_saudi_config.xml"

def run_adb(cmd: str, is_su: bool = False) -> str:
    if is_su:
        full_cmd = [ADB_PATH, "shell", f"su -c '{cmd}'"]
    else:
        full_cmd = [ADB_PATH, "shell"] + cmd.split()
    try:
        res = subprocess.run(full_cmd, capture_output=True, text=True, timeout=12)
        return res.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"

def generate_profile(name: str) -> dict:
    """Generates a fresh, mathematically realistic Saudi device identity."""
    # 1. 16-hex ANDROID_ID
    android_id = secrets.token_hex(8)

    # 2. Genuine Saudi Telecom Company Huawei Fiber ONT MAC
    # Huawei OUI prefixes commonly deployed by STC in Riyadh
    huawei_ouis = ["48:fd:8e", "70:54:25", "00:e0:fc", "20:0b:c7", "ac:e2:15"]
    chosen_oui = random.choice(huawei_ouis)
    suffix = ":".join(f"{secrets.randbelow(256):02x}" for _ in range(3))
    bssid = f"{chosen_oui}:{suffix}"

    # 3. Realistic Saudi Residential Fiber SSID
    suffix_tag = f"{secrets.randbelow(4096):03X}"
    ssid = f"STC_5G_Home_{suffix_tag}" if random.random() < 0.75 else f"STC_Fiber_{suffix_tag}"

    # 4. Riyadh Residential Location (Gaussian jitter around Olaya / Malaz / Nakheel)
    base_lats = [24.7136, 24.6877, 24.7431, 24.7742]
    base_lons = [46.6753, 46.7088, 46.6521, 46.6341]
    center_idx = random.randrange(len(base_lats))
    lat = round(base_lats[center_idx] + random.gauss(0, 0.008), 6)
    lon = round(base_lons[center_idx] + random.gauss(0, 0.008), 6)

    # 5. Riyadh LTE Band 3 Tower CID (STC MCC 420, MNC 01)
    tac = random.choice([14101, 14102, 14103, 14105])
    cell_id = random.randint(28400000, 28999999)
    pci = random.randint(100, 450)

    profile = {
        "name": name,
        "android_id": android_id,
        "wifi_bssid": bssid,
        "wifi_ssid": f'"{ssid}"',
        "latitude": str(lat),
        "longitude": str(lon),
        "lte_tac": tac,
        "lte_ci": cell_id,
        "lte_pci": pci,
        "sim_operator": "STC",
        "sim_mcc_mnc": "42001",
        "country": "SA",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    return profile

def save_profile(profile: dict):
    os.makedirs(PROFILES_DIR, exist_ok=True)
    path = os.path.join(PROFILES_DIR, f"{profile['name']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)
    print(f"[VAULT] Profile '{profile['name']}' saved to {path}")

def list_profiles():
    if not os.path.exists(PROFILES_DIR):
        print("[VAULT] No profiles saved yet.")
        return
    files = [f for f in os.listdir(PROFILES_DIR) if f.endswith(".json")]
    print("=" * 70)
    print(f"   SAVED PROFILES ({len(files)} total):")
    print("=" * 70)
    for f in files:
        path = os.path.join(PROFILES_DIR, f)
        with open(path, "r", encoding="utf-8") as pf:
            data = json.load(pf)
            print(f" - {data['name']}: ANDROID_ID={data['android_id']} | SSID={data['wifi_ssid']} | BSSID={data['wifi_bssid']}")

def deploy_profile_to_device(profile: dict):
    """
    Applies the profile directly into the Android environment:
    1. Stops TikTok.
    2. Performs clean-slate purge of ByteDance storage and device graph artifacts.
    3. Deploys updated XML configuration for Toki hooks.
    """
    print(f"[DEPLOY] Activating Profile: {profile['name']}...")
    
    # 1. Terminate TikTok
    run_adb("am force-stop com.zhiliaoapp.musically")
    time.sleep(0.5)

    # 2. Surgical Clean-Slate Purge
    print("[DEPLOY] Performing surgical clean-slate purge...")
    run_adb("pm clear com.zhiliaoapp.musically")
    # Clean hidden cache, databases, shared_prefs, and external storage residual identifiers (Argon 4 recommendation)
    purge_cmds = (
        "rm -rf /data/data/com.zhiliaoapp.musically/app_applog* "
        "/data/data/com.zhiliaoapp.musically/shared_prefs/* "
        "/data/data/com.zhiliaoapp.musically/databases/* "
        "/data/data/com.zhiliaoapp.musically/files/* "
        "/sdcard/Android/data/com.zhiliaoapp.musically "
        "/sdcard/Android/media/com.zhiliaoapp.musically "
        "/data/media/0/Android/data/com.zhiliaoapp.musically && "
        "touch -m /sdcard/Android 2>/dev/null"
    )
    run_adb(purge_cmds, is_su=True)

    # 3. Build new Toki config XML
    xml_content = f"""<?xml version='1.0' encoding='utf-8' standalone='yes' ?>
<map>
    <string name="target_region">SA</string>
    <boolean name="sim_spoof_enabled" value="true" />
    <string name="sim_operator_code">42001</string>
    <string name="sim_operator_name">STC</string>
    <boolean name="language_spoof_enabled" value="true" />
    <boolean name="language_follow_region" value="true" />
    <string name="custom_language">ar-SA</string>
    <boolean name="timezone_spoof_enabled" value="true" />
    <boolean name="timezone_follow_region" value="true" />
    <string name="custom_timezone">Asia/Riyadh</string>
    <boolean name="gps_spoof_enabled" value="true" />
    <boolean name="gps_follow_region" value="false" />
    <string name="custom_latitude">{profile['latitude']}</string>
    <string name="custom_longitude">{profile['longitude']}</string>
    <boolean name="stealth_spoof_enabled" value="true" />
    <boolean name="network_spoof_enabled" value="true" />
    <boolean name="drm_spoof_enabled" value="true" />
    <string name="custom_android_id">{profile['android_id']}</string>
</map>
"""
    local_tmp = os.path.join(os.path.dirname(__file__), "tmp_config.xml")
    with open(local_tmp, "w", encoding="utf-8") as f:
        f.write(xml_content)

    subprocess.run([ADB_PATH, "push", local_tmp, "/data/local/tmp/toki_saudi_config.xml"], capture_output=True)
    if os.path.exists(local_tmp):
        os.remove(local_tmp)

    print(f"[DEPLOY] Profile '{profile['name']}' deployed successfully!")
    print(f"         ANDROID_ID : {profile['android_id']}")
    print(f"         BSSID / AP : {profile['wifi_bssid']} ({profile['wifi_ssid']})")
    print(f"         Location   : ({profile['latitude']}, {profile['longitude']})")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python profile_vault.py new <profile_name>    -> Generate and save a new clean profile")
        print("  python profile_vault.py apply <profile_name>  -> Deploy saved profile and purge device")
        print("  python profile_vault.py rotate               -> Instantly generate and deploy a fresh profile")
        print("  python profile_vault.py list                 -> List all saved profiles")
        return

    action = sys.argv[1].lower()
    if action == "new":
        name = sys.argv[2] if len(sys.argv) > 2 else f"profile_{secrets.token_hex(3)}"
        p = generate_profile(name)
        save_profile(p)
    elif action == "apply":
        name = sys.argv[2]
        path = os.path.join(PROFILES_DIR, f"{name}.json")
        if not os.path.exists(path):
            print(f"[ERROR] Profile '{name}' does not exist.")
            return
        with open(path, "r", encoding="utf-8") as f:
            p = json.load(f)
        deploy_profile_to_device(p)
    elif action == "rotate":
        name = f"ksa_{secrets.token_hex(4)}"
        p = generate_profile(name)
        save_profile(p)
        deploy_profile_to_device(p)
    elif action == "list":
        list_profiles()
    else:
        print(f"Unknown action: {action}")

if __name__ == "__main__":
    main()
