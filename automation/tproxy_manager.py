#!/usr/bin/env python3
"""
KSA TikTok Phase-4 Enterprise Zero-Interface TPROXY Manager (tproxy_manager.py)
Orchestrates sing-box transparent proxy engine (TPROXY) without creating any tun0 interface.
"""

import subprocess
import json
import time
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(SCRIPT_DIR, "..", "research", "tools")
LOCAL_CONFIG = os.path.join(TOOLS_DIR, "singbox_config.json")
REMOTE_SCRIPT = "/data/local/tmp/95-singbox-tproxy.sh"
REMOTE_CONFIG = "/data/local/tmp/singbox_config.json"
REMOTE_BIN = "/data/local/tmp/sing-box"

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

def run_adb(cmd: str, is_su: bool = True) -> str:
    if is_su:
        full = [ADB_PATH, "shell", f"su -c '{cmd}'"]
    else:
        full = [ADB_PATH, "shell"] + cmd.split()
    try:
        res = subprocess.run(full, capture_output=True, text=True, timeout=12)
        return res.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"

def push_file(local_path: str, remote_path: str):
    subprocess.run([ADB_PATH, "push", local_path, remote_path], capture_output=True)
    run_adb(f"chmod 755 {remote_path}")

def update_proxy_credentials(proxy_type: str, server: str, port: int, user: str = None, password: str = None):
    """Updates singbox_config.json with upstream residential proxy details."""
    if not os.path.exists(LOCAL_CONFIG):
        print(f"[!] Local config not found: {LOCAL_CONFIG}")
        return False

    with open(LOCAL_CONFIG, "r", encoding="utf-8") as f:
        conf = json.load(f)

    outbound = {
        "type": proxy_type,
        "tag": "proxy",
        "server": server,
        "server_port": int(port)
    }
    if user and password:
        if proxy_type == "socks":
            outbound["username"] = user
            outbound["password"] = password
        elif proxy_type == "shadowsocks":
            outbound["method"] = user # e.g. aes-256-gcm or 2022-blake3-aes-128-gcm
            outbound["password"] = password

    # Replace proxy outbound
    for i, out in enumerate(conf.get("outbounds", [])):
        if out.get("tag") == "proxy":
            conf["outbounds"][i] = outbound
            break
    else:
        conf["outbounds"].append(outbound)

    # Ensure route points to proxy
    conf.setdefault("route", {})["final"] = "proxy"
    conf["route"]["default_domain_resolver"] = "remote-dns"
    for s in conf.get("dns", {}).get("servers", []):
        if s.get("tag") == "remote-dns":
            s["detour"] = "proxy"

    with open(LOCAL_CONFIG, "w", encoding="utf-8") as f:
        json.dump(conf, f, indent=2)

    print(f"[+] Updated upstream proxy configuration: {proxy_type}://{server}:{port}")
    push_file(LOCAL_CONFIG, REMOTE_CONFIG)
    return True

def set_direct_mode():
    """Configures sing-box to route all intercepted traffic directly (0 TUN / No Proxy)."""
    if not os.path.exists(LOCAL_CONFIG):
        print(f"[!] Local config not found: {LOCAL_CONFIG}")
        return False

    with open(LOCAL_CONFIG, "r", encoding="utf-8") as f:
        conf = json.load(f)

    conf.setdefault("route", {})["final"] = "direct"
    conf["route"]["default_domain_resolver"] = "local-dns"
    for s in conf.get("dns", {}).get("servers", []):
        s.pop("detour", None)

    with open(LOCAL_CONFIG, "w", encoding="utf-8") as f:
        json.dump(conf, f, indent=2)

    print("[+] Configured sing-box in DIRECT MODE (All traffic routed directly via wlan0, 0 TUN).")
    push_file(LOCAL_CONFIG, REMOTE_CONFIG)
    return True

def cmd_start():
    print("[*] Starting Zero-Interface TPROXY Engine...")
    out = run_adb(f"{REMOTE_SCRIPT} start")
    print(out)

def cmd_stop():
    print("[*] Stopping Zero-Interface TPROXY Engine...")
    out = run_adb(f"{REMOTE_SCRIPT} stop")
    print(out)

def cmd_status():
    out = run_adb(f"{REMOTE_SCRIPT} status")
    print(out)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "start":
            cmd_start()
        elif action == "stop":
            cmd_stop()
        elif action == "status":
            cmd_status()
        elif action == "set" and len(sys.argv) >= 5:
            # python tproxy_manager.py set socks5 1.2.3.4 1080 [user] [pass]
            ptype = sys.argv[2].replace("socks5", "socks")
            server = sys.argv[3]
            port = int(sys.argv[4])
            user = sys.argv[5] if len(sys.argv) > 5 else None
            pwd = sys.argv[6] if len(sys.argv) > 6 else None
            update_proxy_credentials(ptype, server, port, user, pwd)
        elif action in ["direct", "set-direct"]:
            set_direct_mode()
        else:
            print("Usage: tproxy_manager.py {start|stop|status|direct|set <type> <server> <port> [user] [pass]}")
    else:
        cmd_status()
