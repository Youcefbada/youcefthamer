#!/usr/bin/env python3
"""
KSA TikTok Phase-4 Enterprise Human-Biometric & Behavioral Entropy Engine (ksa_human_agent.py)
Directly commands Samsung Galaxy A02's hardware digitizer (/dev/input/event3 'sec_touchscreen')
via compiled on-device DEX driver (touch_driver.jar) emitting real Linux Multi-Touch Type B events.

Hardened against ByteDance ML Behavioral Detection (MetaSec / libmetasec_ml.so):
1. Bimodal Log-Normal Dwell Time Distribution (Skip Mode t < 2.4s vs Engaged Mode t in [9s, 48s]).
2. 2D Postural Drift (Ornstein-Uhlenbeck random walk on thumb coordinates to destroy static KDE heatmaps).
3. Environmental & Peripheral Micro-Signals (volume adjustments, pause/unpause, avatar checks, back gestures).
4. Physical capacitive contact ellipse deformation (Touch Major 35->115->40, Minor maintaining 1.20-1.32 ratio).
"""

import subprocess
import time
import random
import math
import sys
import os
import re
import logging

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

# Postural state for 2D spatial heatmap drift
class GripState:
    def __init__(self):
        self.base_x = 515.0
        self.base_y = 1260.0

    def update_posture(self):
        # Mean-reverting random walk (Ornstein-Uhlenbeck drift)
        self.base_x += 0.3 * (515.0 - self.base_x) + random.gauss(0, 8.0)
        self.base_y += 0.3 * (1260.0 - self.base_y) + random.gauss(0, 14.0)
        self.base_x = max(460.0, min(self.base_x, 570.0))
        self.base_y = max(1160.0, min(self.base_y, 1360.0))

grip = GripState()

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
    """Executes a true hardware capacitive swipe on /dev/input/event3."""
    cmd = f"app_process -Djava.class.path={DRIVER_JAR} /data/local/tmp io.github.meiyongai.toki.touch.TouchDriver swipe {x1:.1f} {y1:.1f} {x2:.1f} {y2:.1f} {duration_ms}"
    run_adb(cmd, is_su=True)

def execute_hw_tap(x: int, y: int):
    """Executes a true hardware capacitive tap on /dev/input/event3."""
    cmd = f"app_process -Djava.class.path={DRIVER_JAR} /data/local/tmp io.github.meiyongai.toki.touch.TouchDriver tap {x} {y}"
    run_adb(cmd, is_su=True)

def execute_bezier_swipe():
    """
    Synthesizes natural right-hand thumb arc coordinates and dispatches
    to the on-device hardware digitizer driver with postural drift.
    """
    grip.update_posture()

    # Start: dynamically drifting lower-right thumb resting area
    x1 = grip.base_x + random.gauss(0, 10.0)
    y1 = grip.base_y + random.gauss(0, 15.0)

    # End: upper-center thumb sweep release point
    x2 = random.uniform(390, 470)
    y2 = random.uniform(320, 440)

    # Duration with log-normal distribution around 240-340ms
    duration_ms = int(random.lognormvariate(math.log(280), 0.15))
    duration_ms = max(200, min(duration_ms, 380))

    execute_hw_swipe(x1, y1, x2, y2, duration_ms)

def double_tap_like():
    """Synthesizes organic double-tap like gesture via hardware digitizer."""
    center_x = 360 + random.randint(-60, 60)
    center_y = 800 + random.randint(-120, 120)
    interval = random.uniform(0.095, 0.140)

    print(f"  [BIO-ACTION] Hardware double-tap like at ({center_x}, {center_y}) interval={int(interval*1000)}ms")
    execute_hw_tap(center_x, center_y)
    time.sleep(interval)
    execute_hw_tap(center_x + random.randint(-4, 4), center_y + random.randint(-4, 4))

def inspect_comments():
    """Simulates opening comment drawer, dwelling, gentle scroll, and dismiss."""
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

def pause_and_resume():
    """Simulates pausing video to observe detail, then unpausing."""
    center_x = 360 + random.randint(-40, 40)
    center_y = 750 + random.randint(-80, 80)
    print("  [BIO-ACTION] Pausing video...")
    execute_hw_tap(center_x, center_y)
    pause_time = random.uniform(1.8, 3.8)
    time.sleep(pause_time)
    print("  [BIO-ACTION] Resuming video...")
    execute_hw_tap(center_x + random.randint(-3, 3), center_y + random.randint(-3, 3))

def inspect_creator_profile():
    """Simulates tapping creator avatar, observing profile for 3-5s, and pressing Back."""
    avatar_x = random.randint(640, 680)
    avatar_y = random.randint(960, 1000)
    print("  [BIO-ACTION] Inspecting creator avatar/profile...")
    execute_hw_tap(avatar_x, avatar_y)
    time.sleep(random.uniform(3.0, 5.2))
    # Android Back keyevent
    run_adb("input keyevent KEYCODE_BACK")

def adjust_media_volume():
    """Simulates realistic hardware volume adjustment."""
    key = "KEYCODE_VOLUME_UP" if random.random() < 0.6 else "KEYCODE_VOLUME_DOWN"
    print(f"  [BIO-ACTION] Peripheral micro-signal: {key}")
    run_adb(f"input keyevent {key}")

def follow_creator():
    """Simulates tapping follow button on creator profile or sidebar."""
    # Profile follow button or right-rail follow plus icon
    follow_x = random.randint(645, 675)
    follow_y = random.randint(1015, 1040)
    print("  [BIO-ACTION] Executing organic follow action...")
    execute_hw_tap(follow_x, follow_y)
    # Argon 4 threshold: never follow faster than 1 every 15s
    time.sleep(random.uniform(16.0, 22.0))

def search_trending_hashtag():
    """Simulates opening TikTok search and browsing a trending Saudi hashtag."""
    SAUDI_HASHTAGS = ["السعودية", "الرياض", "موضة", "طبخ_سعودي", "كوميديا", "رياضة", "جدة", "مكة"]
    tag = random.choice(SAUDI_HASHTAGS)
    print(f"  [BIO-ACTION] Searching trending Saudi hashtag: #{tag}")
    # Tap search/discover icon (bottom nav)
    execute_hw_tap(random.randint(130, 170), random.randint(1530, 1560))
    time.sleep(random.uniform(2.0, 3.0))
    # Tap search bar
    execute_hw_tap(random.randint(300, 420), random.randint(80, 120))
    time.sleep(1.5)
    # Type hashtag via ADB input
    run_adb(f"input text '#{tag}'")
    time.sleep(1.5)
    run_adb("input keyevent 66")  # ENTER / IME_ACTION
    time.sleep(random.uniform(4.0, 8.0))
    # Scroll through search results
    execute_bezier_swipe()
    time.sleep(random.uniform(3.0, 6.0))
    # Return to For You feed
    run_adb("input keyevent KEYCODE_BACK")
    time.sleep(1.0)
    run_adb("input keyevent KEYCODE_BACK")

def open_share_sheet():
    """Opens share sheet and dismisses — generates organic share intent signal without sending."""
    share_x = random.randint(645, 680)
    share_y = random.randint(1140, 1180)
    print("  [BIO-ACTION] Opening share sheet (organic share intent signal)...")
    execute_hw_tap(share_x, share_y)
    time.sleep(random.uniform(1.5, 2.8))
    # Dismiss share sheet without actually sharing
    run_adb("input keyevent KEYCODE_BACK")

# Action counters to strictly enforce Argon 4 TIER_0 through TIER_3 daily safety limits
SESSION_STATS = {
    "likes": 0,
    "follows": 0,
    "comments": 0,
    "profile_checks": 0,
    "volume_adjusts": 0,
    "total_dwell_sec": 0.0
}

# Trust Tier Limits per Argon 4 Empirical Behavioral Vectors
TIER_LIMITS = {
    -1: {  # Silent Ingestion (Day 1 Pure Observation — Zero Engagement)
        "max_likes": 0,
        "max_follows": 0,
        "max_comments": 0,
        "max_profiles": 5,
        "max_session_min": 20.0
    },
    0: {  # Hours 0-24: Untrusted / Evaluation Sandbox
        "max_likes": 15,
        "max_follows": 6,
        "max_comments": 2,
        "max_profiles": 20,
        "max_session_min": 25.0
    },
    1: {  # Hours 24-48: Active Consumer Trust Tier
        "max_likes": 45,
        "max_follows": 18,
        "max_comments": 6,
        "max_profiles": 60,
        "max_session_min": 60.0
    },
    2: {  # Hours 48-96: Trusted Consumer
        "max_likes": 80,
        "max_follows": 35,
        "max_comments": 15,
        "max_profiles": 120,
        "max_session_min": 90.0
    },
    3: {  # Hours 96+: Established Creator
        "max_likes": 150,
        "max_follows": 60,
        "max_comments": 30,
        "max_profiles": 200,
        "max_session_min": 120.0
    }
}

def compute_bimodal_dwell() -> tuple:
    """
    Computes dwell time using exact Argon 4 Empirical Log-Normal Distribution:
    ln(T_dwell) ~ N(mu=1.85, sigma^2=0.55) -> sigma = 0.7416
    - Yields median dwell time ≈ 6.35s with heavy right tail (VCR 0.70-1.15).
    - Mode A (22% Fast-Skip): Dwell in [1.6s, 2.8s] (strictly > 1.5s to avoid programmatic scraper flag)
    - Mode B (78% Engaged Consumption): Truncated log-normal with mu=1.85, sigma=0.7416 (meets >60% VCR criterion)
    """
    is_engaged = random.random() < 0.78
    if is_engaged:
        # Argon 4 Log-Normal formula
        duration = random.lognormvariate(1.85, 0.7416)
        # Ensure completion rate meets TIER_0 promotion threshold (min 6.0s, max 42.0s)
        duration = max(6.0, min(duration, 42.0))
        return True, duration
    else:
        # Avoid programmatic scraper flag: never stay under 1.5s on more than 75% items
        duration = random.uniform(1.6, 2.8)
        return False, duration

def simulate_session(num_videos: int = 15, tier: int = 0):
    """Runs a realistic human TikTok session with high behavioral entropy and strict Tier caps."""
    limits = TIER_LIMITS.get(tier, TIER_LIMITS[0])

    # Reset session counters for fresh state each invocation
    for key in SESSION_STATS:
        SESSION_STATS[key] = 0 if isinstance(SESSION_STATS[key], int) else 0.0

    # Setup session file logging for persistence
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"session_{time.strftime('%Y%m%d_%H%M%S')}.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    session_log = logging.getLogger("toki.session")
    session_log.handlers.clear()  # Prevent duplicate handlers on re-invocation
    session_log.addHandler(file_handler)
    session_log.setLevel(logging.INFO)
    session_log.info(f"Session start: {num_videos} videos, TIER_{tier}, limits={limits}")

    print("=" * 70)
    print(f"   STARTING PHASE-4 BEHAVIORAL ENTROPY BIO-AUTOMATION: {num_videos} VIDEOS (TIER_{tier})")
    print("   Touch Driver : /dev/input/event3 (sec_touchscreen Multi-Touch Type B)")
    print("   Distribution : Argon 4 Log-Normal (mu=1.85, sigma=0.7416, Median=6.35s)")
    print(f"   Safety Gate  : TIER_{tier} Limits (Likes<={limits['max_likes']}, Follows<={limits['max_follows']}, Comments<={limits['max_comments']})")
    print("=" * 70)

    ensure_driver()

    print("[INIT] Verifying TikTok application is active...")
    run_adb("am start -n com.zhiliaoapp.musically/com.ss.android.ugc.aweme.splash.SplashActivity")
    time.sleep(4.0)

    for i in range(1, num_videos + 1):
        # Enforce max cumulative dwell duration to avoid >4h continuous streaming flag
        if (SESSION_STATS["total_dwell_sec"] / 60.0) >= limits["max_session_min"]:
            print(f"[GATE] Reached maximum safe cumulative dwell ({limits['max_session_min']}m). Pausing session.")
            break

        is_engaged, watch_duration = compute_bimodal_dwell()
        SESSION_STATS["total_dwell_sec"] += watch_duration

        if is_engaged:
            print(f"[{i:02d}/{num_videos}] [ENGAGED MODE] Watching high-relevance Gulf content for {watch_duration:.1f}s...")
            time.sleep(watch_duration)

            # Probabilistic Markov micro-transitions constrained by Tier limits
            roll = random.random()
            if roll < 0.14 and SESSION_STATS["likes"] < limits["max_likes"]:
                double_tap_like()
                SESSION_STATS["likes"] += 1
                time.sleep(random.uniform(1.2, 2.4))
            elif roll < 0.20 and SESSION_STATS["follows"] < limits["max_follows"]:
                follow_creator()
                SESSION_STATS["follows"] += 1
            elif roll < 0.27 and SESSION_STATS["comments"] < limits["max_comments"]:
                inspect_comments()
                SESSION_STATS["comments"] += 1
                time.sleep(random.uniform(1.0, 2.0))
            elif roll < 0.33:
                pause_and_resume()
                time.sleep(random.uniform(0.8, 1.6))
            elif roll < 0.39 and SESSION_STATS["profile_checks"] < limits["max_profiles"]:
                inspect_creator_profile()
                SESSION_STATS["profile_checks"] += 1
                time.sleep(random.uniform(1.2, 2.2))
            elif roll < 0.43:
                search_trending_hashtag()
                time.sleep(random.uniform(2.0, 4.0))
            elif roll < 0.47:
                open_share_sheet()
                time.sleep(random.uniform(1.0, 2.0))
            
            # 10% chance of subtle media volume micro-adjustment
            if random.random() < 0.10:
                adjust_media_volume()
                SESSION_STATS["volume_adjusts"] += 1
        else:
            print(f"[{i:02d}/{num_videos}] [SKIP MODE] Fast-skipping non-engaging hook after {watch_duration:.1f}s...")
            time.sleep(watch_duration)

        print(f"[{i:02d}/{num_videos}] Executing hardware capacitive Bezier swipe with biological jerk...")
        execute_bezier_swipe()

        # Thermal and RAM safety guards (check every 5 videos)
        if i % 5 == 0:
            batt_raw = run_adb("dumpsys battery | grep temperature")
            temp_m = re.search(r"temperature:\s*(\d+)", batt_raw)
            if temp_m and int(temp_m.group(1)) / 10.0 > 40.0:
                temp_c = int(temp_m.group(1)) / 10.0
                print(f"[THERMAL GUARD] Battery at {temp_c:.1f}\u00b0C (>40\u00b0C)! Cooling pause 120s...")
                session_log.info(f"Thermal guard triggered: {temp_c:.1f}C")
                run_adb("input keyevent KEYCODE_HOME")
                time.sleep(120)
                run_adb("am start -n com.zhiliaoapp.musically/com.ss.android.ugc.aweme.splash.SplashActivity")
                time.sleep(4.0)
            mem_raw = run_adb("cat /proc/meminfo | grep MemAvailable", is_su=True)
            mem_m = re.search(r"MemAvailable:\s*(\d+)", mem_raw)
            if mem_m and int(mem_m.group(1)) / 1024.0 < 250:
                print("[RAM GUARD] Available RAM < 250MB! Dropping caches...")
                session_log.info(f"RAM guard triggered: {int(mem_m.group(1)) / 1024.0:.0f}MB available")
                run_adb("echo 3 > /proc/sys/vm/drop_caches", is_su=True)
                time.sleep(2.0)

        time.sleep(random.uniform(0.45, 0.95))

    # Clean session completion: Background the app to prevent continuous streaming flag
    print("\n[CLEANUP] Backgrounding TikTok app to record organic session boundary...")
    run_adb("input keyevent KEYCODE_HOME")

    print("=" * 70)
    print("   PHASE-4 BIO-AUTOMATION SESSION COMPLETED SUCCESSFULLY")
    summary = f"Dwell={SESSION_STATS['total_dwell_sec']/60:.1f}min | Likes={SESSION_STATS['likes']} | Follows={SESSION_STATS['follows']} | Comments={SESSION_STATS['comments']} | Profiles={SESSION_STATS['profile_checks']}"
    print(f"   Session Summary: {summary}")
    print("=" * 70)
    session_log.info(f"Session complete: {summary}")

if __name__ == "__main__":
    count = 10
    tier = 0
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            pass
    if len(sys.argv) > 2:
        try:
            tier = int(sys.argv[2])
        except ValueError:
            pass
    simulate_session(count, tier)
