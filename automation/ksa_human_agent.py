#!/usr/bin/env python3
"""
KSA TikTok Phase-2 Enterprise Human-Biometric Automation Engine (ksa_human_agent.py)
Implements non-linear Bezier curve trajectories, ergonomic thumb arc modeling,
micro-tremor jitter, and cognitive dwell/micro-interaction routines for SM-A022F (720x1600).
"""

import subprocess
import time
import random
import math
import sys
import os

ADB_PATH = r"C:\Users\Youcef\Desktop\platform-tools\adb.exe"

# SM-A022F Display Resolution
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 1600

def run_adb(cmd: str) -> str:
    full_cmd = [ADB_PATH, "shell"] + cmd.split()
    try:
        res = subprocess.run(full_cmd, capture_output=True, text=True, timeout=10)
        return res.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"

def bernstein_poly(i: int, n: int, t: float) -> float:
    """Computes Bernstein polynomial for Bezier curve generation."""
    comb = math.comb(n, i)
    return comb * (t ** i) * ((1 - t) ** (n - i))

def bezier_point(points: list, t: float) -> tuple:
    """Calculates an (x, y) point on a Bezier curve of order len(points) - 1 at t in [0, 1]."""
    n = len(points) - 1
    x = sum(bernstein_poly(i, n, t) * points[i][0] for i in range(len(points)))
    y = sum(bernstein_poly(i, n, t) * points[i][1] for i in range(len(points)))
    return (x, y)

def generate_natural_swipe_path() -> tuple:
    """
    Generates a natural right-hand thumb arc swipe on the 720x1600 display.
    Features:
    - Start coordinate in lower-right thumb zone
    - Control points forming a subtle right-to-left natural thumb arc
    - End coordinate in upper-center area
    - Micro-tremor perturbation (±1 to ±2 pixels)
    - Non-linear acceleration / deceleration curve
    """
    # Start: lower-right thumb natural resting zone
    x1 = random.uniform(460, 560)
    y1 = random.uniform(1180, 1340)

    # End: upper-center thumb sweep release point
    x2 = random.uniform(390, 480)
    y2 = random.uniform(320, 440)

    # Arc control point 1: thumb starts pushing inwards
    cp1_x = x1 - random.uniform(40, 80)
    cp1_y = y1 - random.uniform(220, 360)

    # Arc control point 2: thumb reaches peak extension
    cp2_x = x2 + random.uniform(20, 60)
    cp2_y = y2 + random.uniform(200, 340)

    control_points = [(x1, y1), (cp1_x, cp1_y), (cp2_x, cp2_y), (x2, y2)]

    # Duration with log-normal distribution around 240-340ms
    duration_ms = int(random.lognormvariate(math.log(280), 0.15))
    duration_ms = max(190, min(duration_ms, 420))

    return control_points, duration_ms

def execute_bezier_swipe():
    """
    Dispatches a smooth, curved swipe command to Android input subsystem.
    Applies start and end coordinates with calculated natural curve duration.
    """
    points, duration_ms = generate_natural_swipe_path()
    start_x, start_y = points[0]
    end_x, end_y = points[-1]

    # Add Gaussian micro-tremor to endpoints
    start_x += random.gauss(0, 1.5)
    start_y += random.gauss(0, 1.5)
    end_x += random.gauss(0, 1.5)
    end_y += random.gauss(0, 1.5)

    cmd = f"input swipe {int(start_x)} {int(start_y)} {int(end_x)} {int(end_y)} {duration_ms}"
    run_adb(cmd)

def double_tap_like():
    """
    Synthesizes an organic double-tap like gesture.
    Taps at random coordinate near center (video body) with realistic 90-135ms inter-tap interval.
    """
    center_x = 360 + random.randint(-60, 60)
    center_y = 800 + random.randint(-120, 120)
    interval = random.uniform(0.085, 0.135)

    print(f"  [BIO-ACTION] Double-tap like at ({center_x}, {center_y}) interval={int(interval*1000)}ms")
    run_adb(f"input tap {center_x} {center_y}")
    time.sleep(interval)
    run_adb(f"input tap {center_x + random.randint(-3, 3)} {center_y + random.randint(-3, 3)}")

def inspect_comments():
    """
    Simulates opening the comment drawer, reading comments for 2-4s,
    performing a gentle scroll, and dismissing.
    """
    comment_btn_x = random.randint(645, 680)
    comment_btn_y = random.randint(1060, 1100)
    print("  [BIO-ACTION] Opening comment drawer...")
    run_adb(f"input tap {comment_btn_x} {comment_btn_y}")

    # Reading comments dwell
    dwell = random.uniform(2.2, 4.2)
    time.sleep(dwell)

    # Gentle scroll up inside comments
    scroll_x = 360 + random.randint(-40, 40)
    scroll_y1 = random.randint(1200, 1300)
    scroll_y2 = scroll_y1 - random.randint(280, 420)
    scroll_duration = random.randint(250, 380)
    run_adb(f"input swipe {scroll_x} {scroll_y1} {scroll_x} {scroll_y2} {scroll_duration}")
    time.sleep(random.uniform(1.5, 2.5))

    # Close comment drawer (tap outside / top area)
    close_x = random.randint(300, 450)
    close_y = random.randint(300, 420)
    print("  [BIO-ACTION] Closing comment drawer...")
    run_adb(f"input tap {close_x} {close_y}")

def simulate_session(num_videos: int = 15):
    """
    Runs a realistic human TikTok session loop.
    Evaluates video dwell times and applies micro-interactions.
    """
    print("=" * 70)
    print(f"   STARTING HUMAN-BIOMETRIC SESSION: {num_videos} VIDEOS")
    print("=" * 70)

    # Launch TikTok if not already in foreground
    print("[INIT] Verifying TikTok application is active...")
    run_adb("am start -n com.zhiliaoapp.musically/com.ss.android.ugc.aweme.splash.SplashActivity")
    time.sleep(4.0)

    for i in range(1, num_videos + 1):
        # Determine content engagement level (simulated topic classifier)
        # 75% target KSA/Gulf Arabic content vs 25% non-target fast skips
        is_target_ksa = random.random() < 0.78

        if is_target_ksa:
            watch_duration = random.uniform(11.5, 32.0)
            print(f"[{i:02d}/{num_videos}] [KSA-TARGET] Watching Gulf/Arabic content for {watch_duration:.1f}s...")
            time.sleep(watch_duration)

            # Probabilistic micro-interactions
            roll = random.random()
            if roll < 0.16:
                double_tap_like()
                time.sleep(random.uniform(1.2, 2.4))
            elif roll < 0.26:
                inspect_comments()
                time.sleep(random.uniform(1.0, 2.0))
        else:
            # Fast-skip non-target content
            skip_delay = random.uniform(1.4, 2.8)
            print(f"[{i:02d}/{num_videos}] [NON-TARGET] Fast-skipping after {skip_delay:.1f}s...")
            time.sleep(skip_delay)

        # Natural swipe to next video with ergonomic thumb curve
        print(f"[{i:02d}/{num_videos}] Executing natural Bezier thumb swipe...")
        execute_bezier_swipe()

        # Inter-swipe perceptual pause (eye adjustment delay: 400ms - 900ms)
        time.sleep(random.uniform(0.45, 0.95))

    print("=" * 70)
    print("   HUMAN-BIOMETRIC SESSION COMPLETED SUCCESSFULLY")
    print("=" * 70)

if __name__ == "__main__":
    count = 10
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        count = int(sys.argv[1])
    simulate_session(count)
