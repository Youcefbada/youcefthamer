#!/usr/bin/env python3
"""
================================================================================
  KSA TIMED ORGANIC SESSION RUNNER (ksa_timed_session.py)
  Automated Lifecycle:
    1. Turn on Wi-Fi
    2. Auto-connect Saudi VPN (Urban VPN / tun0 verification)
    3. Run TikTok organic guest warm-up for (duration - 2) minutes
    4. 2 minutes before the end:
       - Force-stop TikTok
       - Force-stop VPN
       - Turn off Wi-Fi
       - Wait remaining 2 minutes
       - Turn off screen (sleep)
================================================================================
"""

import sys
import os
import time
import argparse
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, ROOT_DIR)

from automation.adb_utils import run_adb, ADB_PATH
from automation.vpn_manager import cmd_connect, cmd_disconnect, check_tun0, get_ip_info
from automation.guest_warmup import (
    ensure_driver,
    check_and_dismiss_modals,
    execute_bezier_swipe,
    compute_dwell,
    adjust_volume,
    pause_and_resume
)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True, encoding="utf-8")
    except Exception:
        pass


def wake_and_prepare():
    print("[1/5] Waking device & enabling Wi-Fi...")
    run_adb("input keyevent 224") # Wakeup
    run_adb("wm dismiss-keyguard")
    run_adb("svc wifi enable")
    time.sleep(3.0)


def ensure_saudi_vpn() -> bool:
    print("[2/5] Verifying Saudi Arabia VPN connection...")
    if not cmd_connect():
        print("[!] Please ensure VPN is connected to Saudi Arabia manually.")
        return False

    if not check_tun0():
        print("[!] Error: tun0 is not active.")
        return False

    ip_data = get_ip_info()
    cc = ip_data.get("countryCode")
    query = ip_data.get("query")
    city = ip_data.get("city")
    print(f"  -> Exit IP: {query} | Country: {cc} ({city})")

    if cc != "SA":
        print(f"[!] Warning: Exit country is {cc}, expected SA! Aborting.")
        return False

    print("[+] Verified: 100% routed through Saudi Arabia!")
    return True


def run_timed_warmup(warmup_duration_sec: float):
    print(f"[3/5] Starting Organic TikTok Warm-up (Duration: {warmup_duration_sec/60.0:.1f} minutes)...")
    ensure_driver()

    # Launch TikTok
    print("  -> Launching TikTok...")
    run_adb("am start -n com.zhiliaoapp.musically/com.ss.android.ugc.aweme.splash.SplashActivity")
    time.sleep(5.0)
    check_and_dismiss_modals()

    start_time = time.time()
    videos_swiped = 0

    while (time.time() - start_time) < warmup_duration_sec:
        remaining = warmup_duration_sec - (time.time() - start_time)
        is_engaged, dwell = compute_dwell()
        
        # Don't exceed remaining time
        dwell = min(dwell, remaining)
        if dwell <= 0:
            break

        mode_str = "ENGAGED" if is_engaged else "FAST-SKIP"
        elapsed_min = (time.time() - start_time) / 60.0
        print(f"  [{elapsed_min:04.1f}m | Video {videos_swiped+1:03d}] [{mode_str}] Watching for {dwell:.1f}s (Remaining: {remaining/60.0:.1f}m)...")

        # Natural human viewing interval
        if is_engaged and dwell > 10.0:
            half = dwell / 2.0
            time.sleep(half)
            import random
            roll = random.random()
            if roll < 0.12:
                adjust_volume()
            elif roll < 0.20:
                pause_and_resume()
            time.sleep(dwell - half)
        else:
            time.sleep(dwell)

        check_and_dismiss_modals()

        # Check if still time for a swipe
        if (time.time() - start_time) < warmup_duration_sec:
            execute_bezier_swipe()
            videos_swiped += 1
            time.sleep(1.2)
            check_and_dismiss_modals()

    print(f"[+] Warmup period complete! Swiped {videos_swiped} videos.")


def execute_graceful_shutdown(cooldown_sec: float = 120.0):
    print(f"\n[4/5] Pre-stop Boundary reached! Executing automated shutdown 2 minutes before deadline...")
    print("  -> Closing TikTok...")
    run_adb("am force-stop com.zhiliaoapp.musically")
    time.sleep(1.0)

    print("  -> Disconnecting VPN...")
    cmd_disconnect()
    time.sleep(2.0)

    print("  -> Disabling Wi-Fi...")
    run_adb("svc wifi disable")
    time.sleep(1.0)

    print(f"[5/5] Cooldown period ({cooldown_sec:.0f}s) active before complete stop...")
    time.sleep(cooldown_sec)

    print("  -> Turning off screen (sleep mode)...")
    run_adb("input keyevent 223") # KEYCODE_SLEEP
    print("\n" + "=" * 65)
    print("   TIMED KSA SESSION COMPLETED SAFELY & ORGANICALLY")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(description="KSA Timed TikTok Session Controller")
    parser.add_argument("total_minutes", type=float, nargs="?", default=40.0,
                        help="Total lifecycle duration in minutes (default: 40)")
    parser.add_argument("--stop-before", type=float, default=2.0,
                        help="Minutes before total duration to close TikTok/VPN/WiFi (default: 2)")
    args = parser.parse_args()

    total_sec = args.total_minutes * 60.0
    cooldown_sec = args.stop_before * 60.0
    warmup_sec = max(60.0, total_sec - cooldown_sec)

    print("=" * 65)
    print("       KSA TIKTOK ENTERPRISE - TIMED SESSION CONTROLLER")
    print(f"       Total Duration : {args.total_minutes:.1f} minutes")
    print(f"       Warmup Time    : {warmup_sec/60.0:.1f} minutes")
    print(f"       Shutdown Guard : {args.stop_before:.1f} minutes before stop")
    print("=" * 65)

    wake_and_prepare()

    if not ensure_saudi_vpn():
        print("[!] Aborting session due to VPN failure.")
        sys.exit(1)

    run_timed_warmup(warmup_sec)
    execute_graceful_shutdown(cooldown_sec)


if __name__ == "__main__":
    main()
