#!/usr/bin/env python3
"""
KSA TikTok Phase-3 Enterprise Human-Biometric & Hardware Touch Engine (ksa_human_agent.py)
Directly commands Samsung Galaxy A02's hardware digitizer (/dev/input/event3 'sec_touchscreen')
via compiled on-device DEX driver (touch_driver.jar) emitting real Linux Multi-Touch Type B events.

Eliminates adb shell input signatures:
- deviceId is the physical digitizer (not virtual device -1)
- dynamic touchMajor & touchMinor contact ellipse deformation
- dynamic pressure curve (contact -> compression -> lift-off)
- true 60Hz VSYNC event batching and physiological hand tremor
"""

import subprocess
import time
import random
import math
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
DRIVER_JAR = "/data/local/tmp/touch_driver.jar"
LOCAL_JAR = os.path.join(os.path.dirname(__file__), "..", "research", "tools", "touch_driver.jar")

# SM-A022F Display Resolution
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 1600

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

def ensure_driver():
    """Verifies that the compiled TouchDriver DEX is active on the device."""
    check = run_adb(f"[ -f {DRIVER_JAR} ] && echo OK", is_su=True)
    if "OK" not in check:
        if os.path.exists(LOCAL_JAR):
            subprocess.run([ADB_PATH, "push", LOCAL_JAR, DRIVER_JAR], capture_output=True)
            run_adb(f"chmod 644 {DRIVER_JAR}", is_su=True)

def execute_hw_swipe(x1: float, y1: float, x2: float, y2: float, duration_ms: int):
    """
    Executes a true hardware capacitive swipe on /dev/input/event3.
    """
    cmd = f"app_process -Djava.class.path={DRIVER_JAR} /data/local/tmp io.github.meiyongai.toki.touch.TouchDriver swipe {x1:.1f} {y1:.1f} {x2:.1f} {y2:.1f} {duration_ms}"
    run_adb(cmd, is_su=True)

def execute_hw_tap(x: int, y: int):
    """
    Executes a true hardware capacitive tap on /dev/input/event3.
    """
    cmd = f"app_process -Djava.class.path={DRIVER_JAR} /data/local/tmp io.github.meiyongai.toki.touch.TouchDriver tap {x} {y}"
    run_adb(cmd, is_su=True)

def execute_bezier_swipe():
    """
    Synthesizes natural right-hand thumb arc coordinates and dispatches
    to the on-device hardware digitizer driver.
    """
    # Start: lower-right thumb natural resting zone
    x1 = random.uniform(480, 560)
    y1 = random.uniform(1180, 1340)

    # End: upper-center thumb sweep release point
    x2 = random.uniform(390, 470)
    y2 = random.uniform(320, 440)

    # Duration with log-normal distribution around 240-340ms
    duration_ms = int(random.lognormvariate(math.log(280), 0.15))
    duration_ms = max(200, min(duration_ms, 380))

    execute_hw_swipe(x1, y1, x2, y2, duration_ms)

def double_tap_like():
    """
    Synthesizes organic double-tap like gesture via hardware digitizer.
    """
    center_x = 360 + random.randint(-60, 60)
    center_y = 800 + random.randint(-120, 120)
    interval = random.uniform(0.095, 0.140)

    print(f"  [BIO-ACTION] Hardware double-tap like at ({center_x}, {center_y}) interval={int(interval*1000)}ms")
    execute_hw_tap(center_x, center_y)
    time.sleep(interval)
    execute_hw_tap(center_x + random.randint(-4, 4), center_y + random.randint(-4, 4))

def inspect_comments():
    """
    Simulates opening comment drawer, dwelling, gentle scroll, and dismiss.
    """
    comment_btn_x = random.randint(645, 680)
    comment_btn_y = random.randint(1060, 1100)
    print("  [BIO-ACTION] Opening comment drawer via hardware tap...")
    execute_hw_tap(comment_btn_x, comment_btn_y)

    dwell = random.uniform(2.5, 4.5)
    time.sleep(dwell)

    # Gentle scroll up inside comments
    scroll_x = 360 + random.randint(-30, 30)
    scroll_y1 = random.randint(1200, 1280)
    scroll_y2 = scroll_y1 - random.randint(240, 380)
    scroll_duration = random.randint(240, 360)
    execute_hw_swipe(scroll_x, scroll_y1, scroll_x, scroll_y2, scroll_duration)
    time.sleep(random.uniform(1.5, 2.5))

    # Close comment drawer
    close_x = random.randint(300, 450)
    close_y = random.randint(300, 420)
    print("  [BIO-ACTION] Closing comment drawer...")
    execute_hw_tap(close_x, close_y)

def simulate_session(num_videos: int = 15):
    """
    Runs a realistic human TikTok session loop.
    """
    print("=" * 70)
    print(f"   STARTING PHASE-3 HARDWARE BIO-AUTOMATION: {num_videos} VIDEOS")
    print("   Touch Driver: /dev/input/event3 (sec_touchscreen Multi-Touch Type B)")
    print("=" * 70)

    ensure_driver()

    print("[INIT] Verifying TikTok application is active...")
    run_adb("am start -n com.zhiliaoapp.musically/com.ss.android.ugc.aweme.splash.SplashActivity")
    time.sleep(4.0)

    for i in range(1, num_videos + 1):
        is_target_ksa = random.random() < 0.80

        if is_target_ksa:
            watch_duration = random.uniform(12.0, 32.0)
            print(f"[{i:02d}/{num_videos}] [KSA-TARGET] Watching Gulf/Arabic content for {watch_duration:.1f}s...")
            time.sleep(watch_duration)

            roll = random.random()
            if roll < 0.18:
                double_tap_like()
                time.sleep(random.uniform(1.2, 2.4))
            elif roll < 0.28:
                inspect_comments()
                time.sleep(random.uniform(1.0, 2.0))
        else:
            skip_delay = random.uniform(1.6, 3.0)
            print(f"[{i:02d}/{num_videos}] [NON-TARGET] Fast-skipping after {skip_delay:.1f}s...")
            time.sleep(skip_delay)

        print(f"[{i:02d}/{num_videos}] Executing hardware capacitive Bezier swipe...")
        execute_bezier_swipe()

        time.sleep(random.uniform(0.50, 1.05))

    print("=" * 70)
    print("   PHASE-3 BIO-AUTOMATION SESSION COMPLETED SUCCESSFULLY")
    print("=" * 70)

if __name__ == "__main__":
    count = 10
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        count = int(sys.argv[1])
    simulate_session(count)
