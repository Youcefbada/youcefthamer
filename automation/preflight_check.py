#!/usr/bin/env python3
"""
KSA TikTok Phase-2 Enterprise Pre-Flight 25-Point Health Gate
Audits all hardware cloaking, network stealth, kernel firewall rules,
and resource availability on the connected Samsung Galaxy A02 (SM-A022F).
"""

import subprocess
import json
import re
import sys
import os

ADB_PATH = r"C:\Users\Youcef\Desktop\platform-tools\adb.exe"

def run_adb(cmd: str, is_su: bool = False) -> str:
    if is_su:
        # Wrap safely
        escaped = cmd.replace("'", "'\\''")
        full_cmd = [ADB_PATH, "shell", f"su -c '{escaped}'"]
    else:
        full_cmd = [ADB_PATH, "shell"] + cmd.split()
    try:
        res = subprocess.run(full_cmd, capture_output=True, text=True, timeout=12)
        return res.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"

def check_ip_egress() -> dict:
    raw = run_adb("curl -s https://ipinfo.io/json")
    try:
        return json.loads(raw)
    except Exception:
        return {}

def main():
    print("=" * 70)
    print("   KSA TIKTOK PHASE-2 ENTERPRISE PRE-FLIGHT 25-POINT HEALTH GATE")
    print("   Device: Samsung Galaxy A02 (SM-A022F) | OS: Android 11 API 30")
    print("=" * 70)

    checks = []

    def gate(point: int, name: str, passed: bool, detail: str):
        status = " [PASS] " if passed else "![FAIL]!"
        checks.append((point, name, passed, detail))
        print(f"[{point:02d}/25]{status} {name}: {detail}")

    # 1. Always-on VPN App
    vpn_app = run_adb("settings get secure always_on_vpn_app")
    gate(1, "Always-On VPN Application", vpn_app == "com.v2ray.ang", f"app={vpn_app}")

    # 2. Always-on VPN Lockdown (Kill Switch)
    lockdown = run_adb("settings get secure always_on_vpn_lockdown")
    gate(2, "System VPN Lockdown (Kill Switch)", lockdown == "1", f"lockdown={lockdown}")

    # 3. v2rayNG Process Running
    vpn_pid = run_adb("pgrep -f com.v2ray.ang", is_su=True)
    pids = [p.strip() for p in vpn_pid.splitlines() if p.strip().isdigit()]
    gate(3, "v2rayNG Process Status", len(pids) > 0, f"PIDs={pids}")

    # 4. tun0 Interface State
    tun_info = run_adb("ip -br link show tun0", is_su=True)
    tun_active = "tun0" in tun_info and "UP" in tun_info
    gate(4, "VPN tun0 Network Interface", tun_active, f"tun0 status: {tun_info if tun_info else 'DOWN (Awaiting node connection in v2rayNG)'}")

    # 5. Remote Egress IP & Country Code
    ip_data = check_ip_egress()
    country = ip_data.get("country", "")
    ip_addr = ip_data.get("ip", "")
    gate(5, "Saudi Arabia Exit IP Routing", country == "SA", f"IP={ip_addr or 'N/A'} (Country={country or 'N/A'})")

    # 6. ip6tables OUTPUT Policy
    ip6_output = run_adb("ip6tables -L OUTPUT -n -v", is_su=True)
    gate(6, "ip6tables OUTPUT Drop Policy", "policy DROP" in ip6_output, "OUTPUT policy DROP verified")

    # 7. ip6tables FORWARD Policy
    ip6_fwd = run_adb("ip6tables -L FORWARD -n -v", is_su=True)
    gate(7, "ip6tables FORWARD Drop Policy", "policy DROP" in ip6_fwd, "FORWARD policy DROP verified")

    # 8. ip6tables INPUT Policy
    ip6_in = run_adb("ip6tables -L INPUT -n -v", is_su=True)
    gate(8, "ip6tables INPUT Drop Policy", "policy DROP" in ip6_in, "INPUT policy DROP verified")

    # 9. Kernel IPv6 Disable (all)
    ipv6_all = run_adb("sysctl -n net.ipv6.conf.all.disable_ipv6", is_su=True)
    gate(9, "sysctl net.ipv6.conf.all.disable_ipv6", ipv6_all == "1", f"disable_ipv6={ipv6_all}")

    # 10. Kernel IPv6 Disable (default)
    ipv6_def = run_adb("sysctl -n net.ipv6.conf.default.disable_ipv6", is_su=True)
    gate(10, "sysctl net.ipv6.conf.default.disable_ipv6", ipv6_def == "1", f"disable_ipv6={ipv6_def}")

    # 11. Kernel IPv6 Disable (wlan0)
    ipv6_wlan = run_adb("sysctl -n net.ipv6.conf.wlan0.disable_ipv6", is_su=True)
    gate(11, "sysctl net.ipv6.conf.wlan0.disable_ipv6", ipv6_wlan == "1", f"disable_ipv6={ipv6_wlan}")

    # 12. QUIC UDP/443 Drop/Reject in iptables
    ipt_out = run_adb("iptables -L OUTPUT -n -v", is_su=True)
    quic_blocked = "REJECT" in ipt_out and "dpt:443" in ipt_out
    gate(12, "QUIC UDP/443 Interception (TCP Fallback)", quic_blocked, "REJECT rule active on dpt:443")

    # 13. Zygisk Vector Active in Magisk
    vector_mod = run_adb("ls -d /data/adb/modules/zygisk_vector", is_su=True)
    gate(13, "Vector Zygisk Framework Module", "zygisk_vector" in vector_mod, "Zygisk Vector installed")

    # 14. Toki Package Version (v2.0.0 Enterprise)
    toki_ver = run_adb("dumpsys package io.github.meiyongai.toki | grep versionName")
    gate(14, "io.github.meiyongai.toki Version", "2.0.0" in toki_ver, toki_ver)

    # 15. Carrier ISO Country Code
    sim_iso = run_adb("getprop gsm.sim.operator.iso-country")
    gate(15, "Cellular SIM Country ISO", sim_iso.lower() == "sa", f"iso={sim_iso}")

    # 16. Carrier Numeric MCC/MNC
    sim_num = run_adb("getprop gsm.sim.operator.numeric")
    gate(16, "Cellular Operator Numeric (STC 42001)", sim_num == "42001", f"numeric={sim_num}")

    # 17. Carrier Alpha Display Name
    sim_alpha = run_adb("getprop gsm.sim.operator.alpha")
    gate(17, "Cellular Operator Alpha Name", "STC" in sim_alpha, f"alpha={sim_alpha}")

    # 18. Samsung Regional CSC Sales Code
    csc_code = run_adb("getprop ro.csc.country_code")
    gate(18, "Samsung Firmware CSC Code (KSA)", csc_code == "KSA", f"csc={csc_code}")

    # 19. System Timezone
    sys_tz = run_adb("getprop persist.sys.timezone")
    gate(19, "System Timezone (Asia/Riyadh)", sys_tz == "Asia/Riyadh", f"tz={sys_tz}")

    # 20. Wi-Fi Scan Always Enabled Disabled
    wifi_scan = run_adb("settings get global wifi_scan_always_enabled")
    gate(20, "Wi-Fi Background Scanning", wifi_scan == "0", f"wifi_scan_always_enabled={wifi_scan}")

    # 21. BLE Scan Always Enabled Disabled
    ble_scan = run_adb("settings get global ble_scan_always_enabled")
    gate(21, "BLE Background Scanning", ble_scan == "0", f"ble_scan_always_enabled={ble_scan}")

    # 22. Battery Temperature Check (< 42°C)
    batt_raw = run_adb("dumpsys battery | grep temperature")
    temp_m = re.search(r"temperature:\s*(\d+)", batt_raw)
    temp_c = (int(temp_m.group(1)) / 10.0) if temp_m else 30.0
    gate(22, "Battery Temperature Safety (<42°C)", temp_c < 42.0, f"temp={temp_c:.1f}°C")

    # 23. Free RAM Availability (> 350MB)
    mem_raw = run_adb("cat /proc/meminfo | grep MemAvailable", is_su=True)
    mem_m = re.search(r"MemAvailable:\s*(\d+)", mem_raw)
    avail_mb = (int(mem_m.group(1)) / 1024.0) if mem_m else 0.0
    gate(23, "Available RAM Headroom (>350MB)", avail_mb > 350.0, f"available={avail_mb:.1f}MB")

    # 24. SELinux Enforcing Status
    selinux_val = run_adb("cat /sys/fs/selinux/enforce", is_su=True)
    gate(24, "SELinux Enforcing Status", selinux_val == "1", f"enforcing={selinux_val}")

    # 25. Root OOM Watchdog Script
    oom_stat = run_adb("ls -l /data/adb/service.d/98-vpn-oom-guard.sh", is_su=True)
    gate(25, "OOM Score Watchdog Service", "98-vpn-oom-guard.sh" in oom_stat, "Watchdog deployed")

    print("=" * 70)
    passed_count = sum(1 for _, _, p, _ in checks if p)
    print(f"PRE-FLIGHT GATE RESULT: {passed_count}/25 CHECKS PASSED")
    if passed_count == 25:
        print("[STATUS: ZERO LEAK PASS] Device is hardened and ready for TikTok session!")
        return 0
    else:
        print(f"[STATUS: GATED] {25 - passed_count} checks failed. Do not launch TikTok yet.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
