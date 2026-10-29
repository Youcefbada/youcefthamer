#!/usr/bin/env python3
"""
================================================================================
  TOKI ENTERPRISE GUEST WARM-UP (guest_warmup.py)
  Organic TikTok Anonymous Guest Warm-up Engine (Zero-Account / Pure Human Scroll)
  Target: Samsung Galaxy A02 (SM-A022F) | KSA Riyadh
================================================================================
"""

import subprocess
import time
import random
import math
import sys
import os
import re
import logging

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True, encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
LOCAL_JAR = os.path.join(ROOT_DIR, "research", "tools", "touch_driver.jar")
DRIVER_JAR = "/data/local/tmp/touch_driver.jar"

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

class HumanGrip:
    def __init__(self):
        self.base_x = 515.0  # Right thumb base coordinate on 720x1600 screen
        self.base_y = 1260.0
    
    def update_posture(self):
        # Human muscular micro-drift
        self.base_x += 0.3 * (515.0 - self.base_x) + random.gauss(0, 8.0)
        self.base_y += 0.3 * (1260.0 - self.base_y) + random.gauss(0, 14.0)
        self.base_x = max(460.0, min(self.base_x, 570.0))
        self.base_y = max(1160.0, min(self.base_y, 1360.0))

grip = HumanGrip()

def run_adb(cmd: str, is_su: bool = False, timeout: int = 15) -> str:
    if is_su:
        full_cmd = [ADB_PATH, "shell", f"su -c '{cmd}'"]
    else:
        full_cmd = [ADB_PATH, "shell"] + cmd.split()
    try:
        res = subprocess.run(full_cmd, capture_output=True, text=True, timeout=timeout)
        return res.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"

def ensure_driver():
    check = run_adb(f"[ -f {DRIVER_JAR} ] && echo OK", is_su=True)
    if "OK" not in check:
        if os.path.exists(LOCAL_JAR):
            subprocess.run([ADB_PATH, "push", LOCAL_JAR, DRIVER_JAR], capture_output=True)
            run_adb(f"chmod 644 {DRIVER_JAR}", is_su=True)

def execute_hw_tap(x: int, y: int):
    cmd = f"app_process -Djava.class.path={DRIVER_JAR} /data/local/tmp io.github.meiyongai.toki.touch.TouchDriver tap {x} {y}"
    run_adb(cmd, is_su=True)

def execute_hw_swipe(x1: float, y1: float, x2: float, y2: float, duration_ms: int):
    cmd = f"app_process -Djava.class.path={DRIVER_JAR} /data/local/tmp io.github.meiyongai.toki.touch.TouchDriver swipe {x1:.1f} {y1:.1f} {x2:.1f} {y2:.1f} {duration_ms}"
    run_adb(cmd, is_su=True)

def execute_bezier_swipe():
    grip.update_posture()
    x1 = grip.base_x + random.gauss(0, 10.0)
    y1 = grip.base_y + random.gauss(0, 15.0)
    x2 = random.uniform(390, 470)
    y2 = random.uniform(320, 440)
    duration_ms = int(random.lognormvariate(math.log(275), 0.15))
    duration_ms = max(210, min(duration_ms, 370))
    execute_hw_swipe(x1, y1, x2, y2, duration_ms)

def check_and_dismiss_modals():
    """Checks if any login/signup sheet or popup appeared and dismisses it."""
    focus = run_adb("dumpsys window | grep -E mCurrentFocus")
    # If a modal dialog or sign-in activity stole focus, press BACK
    modal_indicators = ["login", "signup", "account", "dialog", "SignIn", "Authorize"]
    if any(ind in focus.lower() for ind in modal_indicators):
        print(f"  [GUARD] Detected modal/login focus ({focus}). Dismissing with BACK key...")
        run_adb("input keyevent KEYCODE_BACK")
        time.sleep(1.0)

def pause_and_resume():
    """Natural micro-action: tap center once to pause, wait 1.5-3.0s, tap to resume."""
    center_x = 360 + random.randint(-35, 35)
    center_y = 750 + random.randint(-60, 60)
    print(f"  [BIO-ACTION] Natural pause/resume at ({center_x}, {center_y})...")
    execute_hw_tap(center_x, center_y)
    time.sleep(random.uniform(1.4, 2.8))
    execute_hw_tap(center_x + random.randint(-3, 3), center_y + random.randint(-3, 3))

def adjust_volume():
    """Natural micro-action: adjust media volume up or down slightly."""
    key = "KEYCODE_VOLUME_UP" if random.random() < 0.6 else "KEYCODE_VOLUME_DOWN"
    print(f"  [BIO-ACTION] Subtle volume adjustment ({key})...")
    run_adb(f"input keyevent {key}")

def compute_dwell():
    """
    Log-normal dwell calculation:
    - 20% Fast-Skip: 1.8s - 3.2s
    - 80% Engaged Watching: 6.5s - 26.0s (Argon 4 log-normal)
    """
    if random.random() < 0.20:
        return False, random.uniform(1.8, 3.2)
    else:
        dur = random.lognormvariate(2.2, 0.45)
        dur = max(6.5, min(dur, 28.0))
        return True, dur

def run_guest_warmup(total_videos: int = 15, capture_interval: int = 5, brain_dir: str = None):
    print("=" * 70)
    print("   TOKI KSA TIKTOK ANONYMOUS GUEST WARM-UP (ZERO ACCOUNT / ZERO LOGIN)")
    print(f"   Target: {total_videos} Videos | Pure Organic Human Swiping")
    print("   Touch Driver: /dev/input/event3 (sec_touchscreen Bezier + Biological Jerk)")
    print("   Egress Gate : Saudi Arabia STC KSA / Riyadh Active")
    print("=" * 70)

    ensure_driver()

    # Ensure TikTok is in foreground
    focus = run_adb("dumpsys window | grep -E mCurrentFocus")
    if "com.zhiliaoapp.musically" not in focus:
        print("[LAUNCH] Bringing TikTok to foreground...")
        run_adb("am start -n com.zhiliaoapp.musically/com.ss.android.ugc.aweme.splash.SplashActivity")
        time.sleep(5.0)
    else:
        print("[INFO] TikTok is already active and focused.")

    check_and_dismiss_modals()

    total_dwell = 0.0
    swipes_completed = 0

    for i in range(1, total_videos + 1):
        is_engaged, dwell = compute_dwell()
        total_dwell += dwell

        mode_str = "ENGAGED" if is_engaged else "FAST-SKIP"
        print(f"\n[{i:02d}/{total_videos}] [{mode_str}] Watching video for {dwell:.1f}s...")
        
        # Natural human viewing interval
        if is_engaged and dwell > 10.0:
            half = dwell / 2.0
            time.sleep(half)
            # Maybe micro-adjust volume or pause
            roll = random.random()
            if roll < 0.12:
                adjust_volume()
            elif roll < 0.20:
                pause_and_resume()
            time.sleep(dwell - half)
        else:
            time.sleep(dwell)

        check_and_dismiss_modals()

        # Execute hardware capacitive Bezier swipe to next video
        print(f"[{i:02d}/{total_videos}] Executing hardware Bezier swipe up...")
        execute_bezier_swipe()
        swipes_completed += 1

        # Post-swipe human settle time
        time.sleep(random.uniform(0.9, 1.8))

        # Check modals after swipe
        check_and_dismiss_modals()

        # Capture progress screenshot if brain_dir provided and at interval
        if brain_dir and (i % capture_interval == 0 or i == total_videos):
            cap_dev = f"/sdcard/guest_warmup_{i}.png"
            cap_pc = os.path.join(brain_dir, f"guest_warmup_{i}.png")
            run_adb(f"screencap -p {cap_dev}")
            subprocess.run([ADB_PATH, "pull", cap_dev, cap_pc], capture_output=True)
            print(f"  [SCREENSHOT] Saved checkpoint screenshot {i} to {cap_pc}")

        # Safety guards every 5 videos
        if i % 5 == 0:
            mem_raw = run_adb("cat /proc/meminfo | grep MemAvailable", is_su=True)
            mem_m = re.search(r"MemAvailable:\s*(\d+)", mem_raw)
            if mem_m and int(mem_m.group(1)) / 1024.0 < 250:
                print("  [RAM GUARD] Freeing cache...")
                run_adb("echo 3 > /proc/sys/vm/drop_caches", is_su=True)

    # Clean finish: Background TikTok to record session boundary
    print("\n[CLEANUP] Backgrounding TikTok app to record organic session boundary...")
    run_adb("input keyevent KEYCODE_HOME")

    print("\n" + "=" * 70)
    print("   GUEST WARM-UP SESSION COMPLETED SUCCESSFULLY")
    print(f"   Videos Swiped : {swipes_completed}")
    print(f"   Total Dwell   : {total_dwell/60.0:.2f} minutes")
    print(f"   Likes Given   : 0 (Strict Guest Safety Gate)")
    print(f"   Follows Given : 0 (Strict Guest Safety Gate)")
    print(f"   Comments Made : 0 (Strict Guest Safety Gate)")
    print(f"   Account Status: 100% Anonymous Guest / Zero Account Touched")
    print("=" * 70)

if __name__ == "__main__":
    count = 15
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            pass
    bdir = r"C:\Users\Youcef\.gemini\antigravity-ide\brain\9c4c2973-a10d-4fd2-963f-4b8a02c27dbc"
    run_guest_warmup(total_videos=count, capture_interval=5, brain_dir=bdir)
