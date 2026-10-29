#!/usr/bin/env python3
"""
================================================================================
  TOKI ENTERPRISE MASTER CONTROLLER (toki.py)
  Unified Command Center for Samsung Galaxy A02 / TikTok KSA Hardening & Growth
================================================================================
Commands:
  python toki.py status                 - Full 360-degree diagnostic audit (Preflight, IP Quality, RAM, VPN)
  python toki.py debloat                - Freeze 30+ bloatware packages, drop caches, tune CPU governor
  python toki.py warmup [count] [tier]  - Run bio-automation session (TIER_0 through TIER_3 velocity caps)
  python toki.py device-warmup [--quick]- Whole-device organic warm-up (Chrome, Maps, Play Store, YouTube)
  python toki.py vpn [cmd]              - Control VPN daemon (status, connect, disconnect, restart, logs)
  python toki.py tproxy [cmd]           - Manage sing-box Zero-Interface TPROXY engine
  python toki.py sanitize <video.mp4>   - Sanitize video, strip x264 SEI, inject Mac timestamps, push to DCIM
  python toki.py tap <x> <y>            - Test physical capacitive tap with synchronous haptic tremor
  python toki.py swipe <x1> <y1> <x2> <y2> [duration_ms] - Test hardware Bezier swipe with biological jerk
  python toki.py profile [list|rotate]  - Manage and rotate hardware identity vaults
  python toki.py schedule [status|run|reset] - Manage 72-hour organic conditioning lifecycle
  python toki.py integrity              - Audit Play Integrity & TEE Keystore attestation
================================================================================
"""

import subprocess
import argparse
import time
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUTO_DIR = os.path.join(SCRIPT_DIR, "automation")

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def print_banner():
    banner = """
================================================================================
  TOKI ENTERPRISE MASTER CONTROLLER (toki.py)
  KSA Enterprise Ghost & Anti-Detection Automation Engine
  Target: Samsung Galaxy A02 (SM-A022F) | OS: Android 11 | STC KSA
================================================================================
"""
    print(banner)

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

def run_script(script_name: str, args: list = None) -> int:
    target = os.path.join(AUTO_DIR, script_name)
    if not os.path.exists(target):
        print(f"[!] Script not found: {target}")
        return 1
    cmd = [sys.executable, target] + (args or [])
    return subprocess.run(cmd).returncode

def preflight_gate() -> bool:
    """Blocks TikTok session execution if critical egress checks fail."""
    target = os.path.join(AUTO_DIR, "preflight_check.py")
    if not os.path.exists(target):
        print("[!] Preflight script not found, skipping gate.")
        return True
    result = subprocess.run([sys.executable, target], capture_output=True, text=True)
    if "![FAIL]!" in result.stdout and "Exit IP Routing" in result.stdout and any(line for line in result.stdout.splitlines() if "![FAIL]!" in line and "Exit IP" in line):
        print("\n" + "=" * 70)
        print("  [CRITICAL ABORT] Exit IP is NOT Saudi Arabia!")
        print("  Running TikTok sessions in this state will cause instant shadowban.")
        print("  Fix: python toki.py tproxy set --type socks --server <KSA_IP> --port <PORT> --user <U> --password <P>")
        print("=" * 70)
        return False
    return True

def cmd_status(args):
    print("\n[STEP 1/4] Running Comprehensive Pre-Flight Health Audit (28 Checks)...")
    run_script("preflight_check.py")

    print("\n[STEP 2/4] Auditing Egress Network ASN & IP Quality...")
    run_script("ip_quality_checker.py")

    print("\n[STEP 3/4] Checking VPN Interface & Daemon Recovery Status...")
    run_script("vpn_manager.py", ["status"])

    print("\n[STEP 4/4] Auditing MT6739 RAM & Performance Headroom...")
    run_script("device_optimizer.py")

def cmd_debloat(args):
    action = "restore" if args.restore else "debloat"
    run_script("device_optimizer.py", [action] if args.restore else [])

def cmd_warmup(args):
    if not preflight_gate():
        return
    count = str(args.count) if args.count else "10"
    if getattr(args, "guest", False) or args.tier == -1:
        print(f"[*] Launching Anonymous Guest Bio-Automation ({count} videos, Zero-Account, Pure Human Swiping)...")
        run_script("guest_warmup.py", [count])
        return
    tier = str(args.tier) if args.tier is not None else "0"
    print(f"[*] Launching Phase-4 Bio-Automation: {count} videos on TIER_{tier}...")
    run_script("ksa_human_agent.py", [count, tier])

def cmd_device_warmup(args):
    quick_flag = ["--quick"] if getattr(args, "quick", False) else []
    print("[*] Launching Holistic Whole-Device Organic Warm-Up (Chrome, Maps, Play Store, YouTube)...")
    run_script("whole_device_warmup.py", quick_flag)

def cmd_vpn(args):
    sub = args.subcommand or "status"
    run_script("vpn_manager.py", [sub])

def cmd_sanitize(args):
    if not os.path.exists(args.video):
        print(f"[!] Input video file does not exist: {args.video}")
        return 1
    push_flag = ["--push"] if args.push else []
    run_script("video_sanitizer.py", [args.video] + push_flag)

def cmd_tap(args):
    jar = "/data/local/tmp/touch_driver.jar"
    cmd = f"app_process -Djava.class.path={jar} /data/local/tmp io.github.meiyongai.toki.touch.TouchDriver tap {args.x} {args.y}"
    print(f"[*] Executing hardware capacitive tap with haptic tremor at ({args.x}, {args.y})...")
    subprocess.run([ADB_PATH, "shell", f"su -c '{cmd}'"])

def cmd_swipe(args):
    jar = "/data/local/tmp/touch_driver.jar"
    duration = args.duration or 280
    cmd = f"app_process -Djava.class.path={jar} /data/local/tmp io.github.meiyongai.toki.touch.TouchDriver swipe {args.x1} {args.y1} {args.x2} {args.y2} {duration}"
    print(f"[*] Executing hardware capacitive Bezier swipe with biological jerk ({args.x1},{args.y1}) -> ({args.x2},{args.y2}) in {duration}ms...")
    subprocess.run([ADB_PATH, "shell", f"su -c '{cmd}'"])

def cmd_profile(args):
    sub = args.subcommand or "list"
    if sub == "list":
        run_script("profile_vault.py", ["list"])
    elif sub == "rotate":
        run_script("profile_vault.py", ["rotate"])

def cmd_tproxy(args):
    sub = args.subcommand or "status"
    sub_args = [sub]
    if sub == "set" and args.server and args.port:
        sub_args = ["set", args.type or "socks", args.server, str(args.port)]
        if args.user:
            sub_args.append(args.user)
        if args.password:
            sub_args.append(args.password)
    run_script("tproxy_manager.py", sub_args)

def cmd_schedule(args):
    sub = args.subcommand or "status"
    sub_args = [f"--{sub}"]
    if sub == "day" and args.day:
        sub_args = ["--day", str(args.day)]
    run_script("warmup_scheduler.py", sub_args)

def cmd_integrity(args):
    run_script("play_integrity_guard.py")

def cmd_session(args):
    min_val = str(args.minutes or 40.0)
    stop_before = str(args.stop_before or 2.0)
    run_script("ksa_timed_session.py", [min_val, "--stop-before", stop_before])

def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description="Toki Enterprise Master Controller",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # tproxy
    p_tproxy = subparsers.add_parser("tproxy", help="Manage sing-box Zero-Interface TPROXY engine")
    p_tproxy.add_argument("subcommand", nargs="?", default="status", choices=["status", "start", "stop", "direct", "set"])
    p_tproxy.add_argument("--type", choices=["socks", "socks5", "shadowsocks", "vless"], default="socks")
    p_tproxy.add_argument("--server", help="Proxy server host or IP")
    p_tproxy.add_argument("--port", type=int, help="Proxy server port")
    p_tproxy.add_argument("--user", help="Proxy username or shadowsocks method")
    p_tproxy.add_argument("--password", help="Proxy password")
    p_tproxy.set_defaults(func=cmd_tproxy)

    # status
    p_status = subparsers.add_parser("status", help="Run full 360-degree system diagnostic audit")
    p_status.set_defaults(func=cmd_status)

    # debloat
    p_debloat = subparsers.add_parser("debloat", help="Debloat Samsung bloatware & reclaim RAM")
    p_debloat.add_argument("--restore", action="store_true", help="Restore all disabled packages")
    p_debloat.set_defaults(func=cmd_debloat)

    # warmup
    p_warmup = subparsers.add_parser("warmup", help="Run organic human bio-automation session on TikTok")
    p_warmup.add_argument("count", type=int, nargs="?", default=10, help="Number of videos to consume (default: 10)")
    p_warmup.add_argument("tier", type=int, nargs="?", default=0, help="Trust tier (0: hours 0-24, 1: hours 24-48, -1: guest)")
    p_warmup.add_argument("--guest", action="store_true", help="Run anonymous guest warm-up without account creation or login")
    p_warmup.set_defaults(func=cmd_warmup)

    # device-warmup
    p_dev_warmup = subparsers.add_parser("device-warmup", help="Warm up whole device (Chrome, Maps, Play Store, YouTube - Zero TikTok)")
    p_dev_warmup.add_argument("--quick", action="store_true", help="Run accelerated quick warmup cycle")
    p_dev_warmup.set_defaults(func=cmd_device_warmup)

    # vpn
    p_vpn = subparsers.add_parser("vpn", help="Manage VPN autostart daemon & routes")
    p_vpn.add_argument("subcommand", nargs="?", default="status", choices=["status", "connect", "disconnect", "restart", "logs"])
    p_vpn.set_defaults(func=cmd_vpn)

    # sanitize
    p_san = subparsers.add_parser("sanitize", help="Sanitize video for upload and push to DCIM")
    p_san.add_argument("video", type=str, help="Path to input MP4 video file")
    p_san.add_argument("--push", action="store_true", default=True, help="Automatically push sanitized video to DCIM/Camera")
    p_san.set_defaults(func=cmd_sanitize)

    # tap
    p_tap = subparsers.add_parser("tap", help="Test hardware capacitive tap")
    p_tap.add_argument("x", type=int, help="Screen X coordinate")
    p_tap.add_argument("y", type=int, help="Screen Y coordinate")
    p_tap.set_defaults(func=cmd_tap)

    # swipe
    p_swipe = subparsers.add_parser("swipe", help="Test hardware Bezier swipe")
    p_swipe.add_argument("x1", type=float, help="Start X")
    p_swipe.add_argument("y1", type=float, help="Start Y")
    p_swipe.add_argument("x2", type=float, help="End X")
    p_swipe.add_argument("y2", type=float, help="End Y")
    p_swipe.add_argument("duration", type=int, nargs="?", default=280, help="Duration in ms (default: 280)")
    p_swipe.set_defaults(func=cmd_swipe)

    # profile
    p_prof = subparsers.add_parser("profile", help="Manage hardware identity profiles")
    p_prof.add_argument("subcommand", nargs="?", default="list", choices=["list", "rotate"])
    p_prof.set_defaults(func=cmd_profile)

    # schedule
    p_sched = subparsers.add_parser("schedule", help="Manage 72-hour organic conditioning lifecycle")
    p_sched.add_argument("subcommand", nargs="?", default="status", choices=["status", "run", "reset", "day"])
    p_sched.add_argument("--day", type=int, help="Force specific day number (1, 2, or 3)")
    p_sched.set_defaults(func=cmd_schedule)

    # integrity
    p_integrity = subparsers.add_parser("integrity", help="Audit Play Integrity & TEE Keystore attestation")
    p_integrity.set_defaults(func=cmd_integrity)

    # session
    p_session = subparsers.add_parser("session", help="Run automated timed KSA session (Wi-Fi ON -> VPN -> TikTok warm-up -> Stop 2m before -> WiFi OFF -> Sleep)")
    p_session.add_argument("minutes", type=float, nargs="?", default=40.0, help="Total session minutes (default: 40)")
    p_session.add_argument("--stop-before", type=float, default=2.0, help="Minutes before stop to close TikTok/VPN/WiFi (default: 2)")
    p_session.set_defaults(func=cmd_session)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
