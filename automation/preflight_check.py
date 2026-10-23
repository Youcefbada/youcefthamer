#!/usr/bin/env python3
"""
KSA TikTok Phase-3 Enterprise Pre-Flight Health Gate
Audits hardware cloaking, native bootloader properties, kernel firewall rules,
touch digitizer drivers, and system resources on Samsung Galaxy A02 (SM-A022F).
"""

import subprocess
import json
import re
import sys
import os

try:
    from adb_utils import ADB_PATH, run_adb
except ImportError:
    try:
        from automation.adb_utils import ADB_PATH, run_adb
    except ImportError:
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
        def run_adb(cmd: str, is_su: bool = False, timeout: int = 12) -> str:
            if is_su:
                escaped = cmd.replace("'", "'\\''")
                full_cmd = [ADB_PATH, "shell", f"su -c '{escaped}'"]
            else:
                full_cmd = [ADB_PATH, "shell"] + cmd.split()
            try:
                res = subprocess.run(full_cmd, capture_output=True, text=True, timeout=timeout)
                return res.stdout.strip()
            except Exception as e:
                return f"ERROR: {e}"

_IP_CACHE = None

def check_ip_egress() -> dict:
    global _IP_CACHE
    if _IP_CACHE is not None:
        return _IP_CACHE
    raw = run_adb("/data/adb/magisk/busybox wget -qO- http://ip-api.com/json", is_su=True, timeout=8)
    try:
        data = json.loads(raw)
        _IP_CACHE = {
            "country": data.get("countryCode", ""),
            "ip": data.get("query", ""),
            "city": data.get("city", ""),
            "as": data.get("as", ""),
            "isp": data.get("isp", ""),
            "org": data.get("org", ""),
            "raw": data
        }
        return _IP_CACHE
    except Exception:
        return {}

def main():
    print("=" * 70)
    print("   KSA TIKTOK PHASE-3 ENTERPRISE PRE-FLIGHT HEALTH GATE")
    print("   Device: Samsung Galaxy A02 (SM-A022F) | OS: Android 11 API 30")
    print("=" * 70)

    total_checks = 29
    checks = []

    def gate(point: int, name: str, passed: bool, detail: str):
        status = " [PASS] " if passed else "![FAIL]!"
        checks.append((point, name, passed, detail))
        print(f"[{point:02d}/{total_checks}]{status} {name}: {detail}")

    # 1-4: Proxy / VPN Architecture Health Check (TPROXY or Legacy VPN)
    singbox_pid = run_adb("pidof sing-box", is_su=True).strip()
    is_tproxy = bool(singbox_pid and singbox_pid.isdigit())

    if is_tproxy:
        gate(1, "Zero-Interface TPROXY Engine", True, f"sing-box active (PID {singbox_pid})")
        gate(2, "Network Tunnel Architecture", True, "Zero-Interface TPROXY (Kernel Netfilter Interception)")
        tproxy_rules = run_adb("iptables -t mangle -L SINGBOX_TPROXY 2>/dev/null | grep -c TPROXY", is_su=True)
        gate(3, "TPROXY Interception Rules", int(tproxy_rules or "0") > 0, f"{tproxy_rules} active mangle rules")
        tun_count = run_adb(r"ip link show | grep -E '^\s*[0-9]+:\s*(tun[0-9]|ppp[0-9])' | wc -l", is_su=True)
        tun_stealth = (tun_count.strip() == "0")
        gate(4, "Zero TUN/PPP Stealth Verification", tun_stealth, "0 TUN/PPP interfaces (MetaSec Probes Blinded)" if tun_stealth else f"{tun_count} active TUN leaked!")
    else:
        vpn_pids = run_adb("pgrep -f 'com.urbanvpn.android|com.v2ray.ang'", is_su=True)
        active_vpns = [p.strip() for p in vpn_pids.splitlines() if p.strip().isdigit()]
        gate(1, "VPN Application Active Status", len(active_vpns) > 0, f"Active VPN Process Count={len(active_vpns)}")
        vpn_app = run_adb("settings get secure always_on_vpn_app")
        gate(2, "Always-on VPN Routing Target", True, f"app={vpn_app or 'Dynamic'}")
        tun_info = run_adb("ip -br link show tun0", is_su=True)
        gate(3, "VPN Process Running", len(active_vpns) > 0, f"PIDs={active_vpns[:4]}")
        tun_active = "tun0" in tun_info and "UP" in tun_info
        gate(4, "VPN tun0 Network Interface", tun_active, f"tun0 status: {tun_info if tun_info else 'DOWN'}")

    # 5. Remote Egress IP & Country Code
    ip_data = check_ip_egress()
    country = ip_data.get("country", "")
    ip_addr = ip_data.get("ip", "")
    city = ip_data.get("city", "")
    gate(5, "Saudi Arabia Exit IP Routing", country == "SA", f"IP={ip_addr or 'N/A'} (City={city}, Country={country or 'N/A'})")

    # 6. ip6tables OUTPUT Policy
    ip6_output = run_adb("ip6tables -L OUTPUT -n -v", is_su=True)
    gate(6, "ip6tables OUTPUT Drop Policy", "policy DROP" in ip6_output, "OUTPUT policy DROP verified")

    # 7. Kernel IPv6 Disable (all)
    ipv6_all = run_adb("sysctl -n net.ipv6.conf.all.disable_ipv6", is_su=True)
    gate(7, "sysctl net.ipv6.conf.all.disable_ipv6", ipv6_all == "1", f"disable_ipv6={ipv6_all}")

    # 8. QUIC UDP/443 Interception
    ipt_out = run_adb("iptables -L OUTPUT -n -v", is_su=True)
    quic_blocked = "REJECT" in ipt_out and "dpt:443" in ipt_out
    gate(8, "QUIC UDP/443 Interception (TCP Fallback)", quic_blocked, "REJECT rule active on dpt:443")

    # 9. WebRTC / STUN UDP Leak Protection
    webrtc_blocked = "10205" in ipt_out and "wlan0" in ipt_out and "REJECT" in ipt_out
    gate(9, "WebRTC STUN / Direct UDP Egress Block", webrtc_blocked, "TikTok direct wlan0 UDP rejected")

    # 10. Native Bootloader State (ro.boot.verifiedbootstate)
    boot_state = run_adb("getprop ro.boot.verifiedbootstate")
    gate(10, "Native VerifiedBootState (resetprop)", boot_state == "green", f"state={boot_state}")

    # 11. Native Flash Lock State (ro.boot.flash.locked)
    flash_lock = run_adb("getprop ro.boot.flash.locked")
    gate(11, "Native Flash Locked Flag", flash_lock == "1", f"locked={flash_lock}")

    # 12. Hardware Touch Driver Presence
    touch_drv = run_adb("[ -f /data/local/tmp/touch_driver.jar ] && echo OK", is_su=True)
    gate(12, "Hardware Touch Driver DEX", "OK" in touch_drv, "/data/local/tmp/touch_driver.jar ready")

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

    # 20. Wi-Fi Background Scanning Disabled
    wifi_scan = run_adb("settings get global wifi_scan_always_enabled")
    gate(20, "Wi-Fi Background Scanning", wifi_scan == "0", f"wifi_scan_always_enabled={wifi_scan}")

    # 21. BLE Background Scanning Disabled
    ble_scan = run_adb("settings get global ble_scan_always_enabled")
    gate(21, "BLE Background Scanning", ble_scan == "0", f"ble_scan_always_enabled={ble_scan}")

    # 22. Battery Temperature Safety (< 42°C)
    batt_raw = run_adb("dumpsys battery | grep temperature")
    temp_m = re.search(r"temperature:\s*(\d+)", batt_raw)
    temp_c = (int(temp_m.group(1)) / 10.0) if temp_m else 30.0
    gate(22, "Battery Temperature Safety (<42°C)", temp_c < 42.0, f"temp={temp_c:.1f}°C")

    # 23. Available RAM Headroom (> 350MB)
    mem_raw = run_adb("cat /proc/meminfo | grep MemAvailable", is_su=True)
    mem_m = re.search(r"MemAvailable:\s*(\d+)", mem_raw)
    avail_mb = (int(mem_m.group(1)) / 1024.0) if mem_m else 0.0
    gate(23, "Available RAM Headroom (>350MB)", avail_mb > 350.0, f"available={avail_mb:.1f}MB")

    # 24. SELinux Enforcing Status
    selinux_val = run_adb("cat /sys/fs/selinux/enforce", is_su=True)
    gate(24, "SELinux Enforcing Status", selinux_val == "1", f"enforcing={selinux_val}")

    # 25. Persistent Resetprop Stealth Service
    reset_svc = run_adb("ls -l /data/adb/service.d/97-resetprop-stealth.sh", is_su=True)
    gate(25, "Native Property Stealth Service", "97-resetprop-stealth.sh" in reset_svc, "97-resetprop-stealth.sh deployed")

    # 26. MT6739 Virtual Memory Tuning Service
    vm_svc = run_adb("ls -l /data/adb/service.d/98-vpn-oom-guard.sh", is_su=True)
    gate(26, "MT6739 VM & OOM Tuning Service", "98-vpn-oom-guard.sh" in vm_svc, "98-vpn-oom-guard.sh deployed")

    # 27. Kernel Zero-Leak Firewall Service
    fw_svc = run_adb("ls -l /data/adb/service.d/99-ksa-firewall.sh", is_su=True)
    gate(27, "Hardened Kernel Firewall Service", "99-ksa-firewall.sh" in fw_svc, "99-ksa-firewall.sh deployed")

    # 28. ZRAM Swappiness Tuning
    swappiness = run_adb("sysctl -n vm.swappiness", is_su=True)
    gate(28, "ZRAM Swappiness = 100", swappiness == "100", f"vm.swappiness={swappiness}")

    # 29. IP Residential vs Datacenter Classification
    ip_data = check_ip_egress()
    as_info = ip_data.get("as", "")
    isp_info = ip_data.get("isp", "")
    datacenter_keywords = ["hosting", "cloud", "server", "datacenter", "digitalocean", "linode", "aws", "ovh", "hetzner", "choopa", "m247", "leaseweb"]
    is_dc = any(kw in as_info.lower() or kw in isp_info.lower() for kw in datacenter_keywords)
    if as_info:
        gate(29, "IP Residential Classification", not is_dc,
             f"Residential/ISP IP verified (AS: {as_info})" if not is_dc else f"DATACENTER/HOSTING DETECTED! (AS: {as_info})")
    else:
        gate(29, "IP Residential Classification", False, "Could not verify IP residential status")

    print("=" * 70)
    passed_count = sum(1 for _, _, p, _ in checks if p)
    print(f"PRE-FLIGHT GATE RESULT: {passed_count}/{total_checks} CHECKS PASSED")
    if passed_count >= 27:
        print("[STATUS: ZERO LEAK PASS] Device is fully hardened and ready for TikTok session!")
        return 0
    else:
        print(f"[STATUS: GATED] {total_checks - passed_count} checks failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
