#!/usr/bin/env python3
"""
vpn_manager.py - KSA TikTok Enterprise Automated VPN Controller & Watchdog Manager
Controls, deploys, and monitors automated Saudi VPN (Urban VPN / OpenVPN) on Samsung Galaxy A02.
"""

import subprocess
import json
import time
import sys
import os

ADB_CANDIDATES = [
    r"C:\Users\Youcef\AppData\Local\Android\Sdk\platform-tools\adb.exe",
    r"C:\Users\Youcef\Desktop\platform-tools\adb.exe",
    "adb"
]

def find_adb() -> str:
    for c in ADB_CANDIDATES:
        if os.path.exists(c):
            return c
    return "adb"

ADB_PATH = find_adb()

def run_adb(cmd: str, is_su: bool = False, timeout: int = 15) -> str:
    if is_su:
        escaped = cmd.replace("'", "'\\''")
        full_cmd = [ADB_PATH, "shell", f"su -c '{escaped}'"]
    else:
        full_cmd = [ADB_PATH, "shell"] + (cmd.split() if isinstance(cmd, str) else cmd)
    try:
        res = subprocess.run(full_cmd, capture_output=True, text=True, timeout=timeout)
        return res.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"

def get_ip_info() -> dict:
    raw = run_adb("/data/adb/magisk/busybox wget -qO- http://ip-api.com/json", is_su=True)
    if not raw or not raw.startswith("{"):
        raw = run_adb("curl -s http://ip-api.com/json")
    try:
        return json.loads(raw)
    except Exception:
        return {}

def check_tun0() -> bool:
    out = run_adb("ip link show tun0", is_su=True)
    return "UP" in out

def get_vpn_pids() -> list:
    raw = run_adb("pidof com.urbanvpn.android com.v2ray.ang libpie_openvpn", is_su=True)
    return [p.strip() for p in raw.split() if p.strip().isdigit()]

def cmd_status():
    print("=" * 65)
    print("      KSA TIKTOK ENTERPRISE - VPN STATUS & HEALTH")
    print("=" * 65)
    
    tun_active = check_tun0()
    pids = get_vpn_pids()
    always_on = run_adb("settings get secure always_on_vpn_app")
    
    print(f"[*] TUN0 Interface       : {'[UP - ENCRYPTED TUNNEL ACTIVE]' if tun_active else '[DOWN - NO ACTIVE TUNNEL]'}")
    print(f"[*] VPN Engine PIDs       : {pids if pids else 'None'}")
    print(f"[*] Always-On VPN Setting : {always_on or 'Not set'}")
    
    print("[*] Fetching Public IP Information...")
    ip_data = get_ip_info()
    if ip_data:
        country = ip_data.get("country", "Unknown")
        country_code = ip_data.get("countryCode", "??")
        city = ip_data.get("city", "Unknown")
        query = ip_data.get("query", "Unknown")
        isp = ip_data.get("isp", "Unknown")
        print(f"    - Public IP     : {query}")
        print(f"    - Exit Country  : {country} ({country_code})")
        print(f"    - Exit City     : {city}")
        print(f"    - Internet ISP  : {isp}")
        if country_code == "SA":
            print("\n>>> STATUS: [OPTIMAL] Traffic is 100% routed through Saudi Arabia! <<<")
        else:
            print(f"\n>>> WARNING: Traffic routed through {country_code}, NOT Saudi Arabia! <<<")
    else:
        print("    [!] Could not query external IP (Tunnel might be establishing or network down).")
    print("=" * 65)

def cmd_connect():
    print("[*] Checking Saudi VPN status on device...")
    if check_tun0():
        ip_data = get_ip_info()
        if ip_data.get("countryCode") == "SA":
            print(f"[+] VPN is active and routed to Saudi Arabia ({ip_data.get('query')})!")
            return True
        else:
            print(f"[!] VPN is active but routed to {ip_data.get('countryCode')} (not SA).")
            return False
    else:
        print("[!] VPN tunnel (tun0) is DOWN.")
        print("[i] Automatic Urban VPN launching has been removed. Please launch and connect your VPN manually on the device.")
        return False

def cmd_disconnect():
    print("[*] Disconnecting VPN...")
    run_adb("am force-stop com.urbanvpn.android", is_su=True)
    time.sleep(1)
    print(f"[*] TUN0 Status: {'UP' if check_tun0() else 'DOWN (Disconnected)'}")

def cmd_uninstall_daemon():
    print("[*] Removing any persistent VPN autostart daemon and restoring manual control...")
    run_adb("pkill -9 -f 94-vpn-autostart-daemon.sh", is_su=True)
    run_adb("rm -f /data/adb/service.d/94-vpn-autostart-daemon.sh", is_su=True)
    run_adb("rm -f /data/local/tmp/94-vpn-autostart-daemon.sh /data/local/tmp/vpn_autostart.log /data/local/tmp/urban_ui*.xml", is_su=True)
    run_adb("settings delete secure always_on_vpn_app", is_su=True)
    run_adb("settings put secure always_on_vpn_lockdown 0", is_su=True)
    print("[+] Autostart daemon completely removed. Device is restored to standard manual VPN control.")

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:
        print("Usage: python automation/vpn_manager.py <command>")
        print("\nCommands:")
        print("  status            Show current VPN tunnel, processes, and exit IP")
        print("  disconnect        Disconnect VPN")
        print("  uninstall-daemon  Completely remove background autostart & watchdog daemon from phone")
        return

    cmd = sys.argv[1].lower()
    if cmd == "status":
        cmd_status()
    elif cmd == "connect":
        cmd_connect()
    elif cmd == "disconnect":
        cmd_disconnect()
    elif cmd in ["uninstall-daemon", "remove-daemon"]:
        cmd_uninstall_daemon()
    elif cmd in ["install-daemon", "restart-daemon"]:
        print("[!] Automated VPN autostart daemon has been decommissioned by user request.")
        print("[i] To ensure all background services are removed from your device, run:")
        print("    python automation/vpn_manager.py uninstall-daemon")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
