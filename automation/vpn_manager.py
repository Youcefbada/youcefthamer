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
    raw = run_adb("pgrep -f 'com.urbanvpn.android|libpie_openvpn|com.v2ray.ang'", is_su=True)
    return [p.strip() for p in raw.splitlines() if p.strip().isdigit()]

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
    print("[*] Initiating automated Saudi VPN connection on device...")
    # Check if already connected
    if check_tun0():
        ip_data = get_ip_info()
        if ip_data.get("countryCode") == "SA":
            print(f"[+] VPN is already active and routed to Saudi Arabia ({ip_data.get('query')})!")
            return

    # Trigger connection sequence
    print("[*] Launching Urban VPN...")
    run_adb("monkey -p com.urbanvpn.android -c android.intent.category.LAUNCHER 1")
    time.sleep(2)
    
    print("[*] Dismissing prompts & triggering Connect button...")
    run_adb("input tap 187 1427") # Skip if present
    time.sleep(1)
    run_adb("input tap 359 526")  # Connect button (Saudi Arabia)
    
    print("[*] Waiting for tun0 to initialize...")
    for i in range(15):
        time.sleep(1)
        if check_tun0():
            print(f"[+] tun0 connected after {i+1} seconds!")
            break
    else:
        print("[!] Timeout waiting for tun0. Checking status...")

    # Return to home
    run_adb("input keyevent 3")
    
    # Pin OOM score
    run_adb("for p in $(pgrep -f 'com.urbanvpn.android|libpie_openvpn'); do [ -d /proc/$p ] && echo -900 > /proc/$p/oom_score_adj; done", is_su=True)
    
    cmd_status()

def cmd_disconnect():
    print("[*] Disconnecting VPN...")
    run_adb("am force-stop com.urbanvpn.android", is_su=True)
    time.sleep(2)
    print(f"[*] TUN0 Status: {'UP' if check_tun0() else 'DOWN (Disconnected)'}")

def cmd_install_daemon():
    print("[*] Installing persistent VPN Autostart & Watchdog Daemon onto device...")
    
    script_local = os.path.join(os.path.dirname(__file__), "..", "research", "tools", "94-vpn-autostart-daemon.sh")
    script_local = os.path.abspath(script_local)
    
    if not os.path.exists(script_local):
        print(f"[!] Error: {script_local} does not exist!")
        return

    # Push to device
    print(f"[*] Pushing {os.path.basename(script_local)} to /data/local/tmp/...")
    subprocess.run([ADB_PATH, "push", script_local, "/data/local/tmp/94-vpn-autostart-daemon.sh"], check=True)
    
    # Push updated 98-vpn-oom-guard.sh
    guard_local = os.path.join(os.path.dirname(__file__), "..", "research", "tools", "98-vpn-oom-guard.sh")
    subprocess.run([ADB_PATH, "push", guard_local, "/data/local/tmp/98-vpn-oom-guard.sh"], check=True)

    # Install into Magisk service.d
    print("[*] Deploying to Magisk /data/adb/service.d/...")
    deploy_cmd = (
        "cp /data/local/tmp/94-vpn-autostart-daemon.sh /data/adb/service.d/94-vpn-autostart-daemon.sh && "
        "chmod 755 /data/adb/service.d/94-vpn-autostart-daemon.sh && "
        "cp /data/local/tmp/98-vpn-oom-guard.sh /data/adb/service.d/98-vpn-oom-guard.sh && "
        "chmod 755 /data/adb/service.d/98-vpn-oom-guard.sh && "
        "settings put secure always_on_vpn_app com.urbanvpn.android"
    )
    res = run_adb(deploy_cmd, is_su=True)
    print(f"[+] Magisk service deployment result: {res or 'SUCCESS'}")

    # Start the daemon in background
    cmd_restart_daemon()
    print("[+] Installation complete! VPN will now start automatically whenever the phone boots, opens, or wakes up.")

def cmd_restart_daemon():
    print("[*] Restarting VPN Autostart Watchdog Daemon on device...")
    run_adb("pkill -f 94-vpn-autostart-daemon.sh", is_su=True)
    time.sleep(1)
    run_adb("nohup /data/adb/service.d/94-vpn-autostart-daemon.sh >/dev/null 2>&1 &", is_su=True)
    time.sleep(2)
    pids = run_adb("pgrep -f 94-vpn-autostart-daemon.sh", is_su=True)
    if pids:
        print(f"[+] Watchdog Daemon is running (PID: {pids.splitlines()[0]}).")
    else:
        print("[!] Failed to verify running daemon.")

def cmd_logs():
    print("[*] Retrieving daemon logs (/data/local/tmp/vpn_autostart.log)...")
    logs = run_adb("tail -n 30 /data/local/tmp/vpn_autostart.log", is_su=True)
    print("-" * 65)
    print(logs or "No logs found yet.")
    print("-" * 65)

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:
        print("Usage: python automation/vpn_manager.py <command>")
        print("\nCommands:")
        print("  status          Show current VPN tunnel, processes, and exit IP")
        print("  connect         Automatically launch and connect Saudi VPN")
        print("  disconnect      Disconnect VPN")
        print("  install-daemon  Install persistent Magisk boot & wake watchdog daemon")
        print("  restart-daemon  Restart watchdog daemon on phone")
        print("  logs            Display latest watchdog log entries")
        return

    cmd = sys.argv[1].lower()
    if cmd == "status":
        cmd_status()
    elif cmd == "connect":
        cmd_connect()
    elif cmd == "disconnect":
        cmd_disconnect()
    elif cmd == "install-daemon":
        cmd_install_daemon()
    elif cmd == "restart-daemon":
        cmd_restart_daemon()
    elif cmd == "logs":
        cmd_logs()
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
