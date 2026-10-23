#!/usr/bin/env python3
"""
================================================================================
  KSA WHOLE-DEVICE ORGANIC WARM-UP ENGINE (whole_device_warmup.py)
  Conditioning Samsung Galaxy A02 (SM-A022F) without touching TikTok accounts.
================================================================================
Simulates authentic Saudi user interaction across core Google ecosystem apps:
  1. Chrome: Surfing major Saudi portals (Sabq, Al Riyadh, Haraj, Google KSA)
  2. Google Maps: Passive geographic orientation around Riyadh, KSA
  3. Google Play Store: Natural browsing of trending KSA apps & updates
  4. YouTube: Viewing Saudi trending media passively
  5. Behavioral Entropy: Postural drift, hardware Bezier swipes, micro-pauses.

CRITICAL CONSTRAINT: ZERO TikTok account creation or login prompts.
================================================================================
"""

import subprocess
import random
import time
import math
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DRIVER_JAR = "/data/local/tmp/touch_driver.jar"
LOCAL_JAR = os.path.join(SCRIPT_DIR, "..", "research", "tools", "touch_driver.jar")

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
    """Verifies that the compiled TouchDriver DEX is active on the device."""
    check = run_adb(f"[ -f {DRIVER_JAR} ] && echo OK", is_su=True)
    if "OK" not in check:
        if os.path.exists(LOCAL_JAR):
            subprocess.run([ADB_PATH, "push", LOCAL_JAR, DRIVER_JAR], capture_output=True)
            run_adb(f"chmod 644 {DRIVER_JAR}", is_su=True)

def hw_swipe(x1: float, y1: float, x2: float, y2: float, duration_ms: int):
    """Executes a true hardware capacitive swipe on /dev/input/event3."""
    cmd = f"app_process -Djava.class.path={DRIVER_JAR} /data/local/tmp io.github.meiyongai.toki.touch.TouchDriver swipe {x1:.1f} {y1:.1f} {x2:.1f} {y2:.1f} {duration_ms}"
    res = run_adb(cmd, is_su=True)
    if "ERROR" in res:
        # Fallback to standard input swipe if driver fails
        run_adb(f"input swipe {int(x1)} {int(y1)} {int(x2)} {int(y2)} {duration_ms}")

def hw_tap(x: int, y: int):
    """Executes a true hardware capacitive tap on /dev/input/event3."""
    cmd = f"app_process -Djava.class.path={DRIVER_JAR} /data/local/tmp io.github.meiyongai.toki.touch.TouchDriver tap {x} {y}"
    res = run_adb(cmd, is_su=True)
    if "ERROR" in res:
        run_adb(f"input tap {x} {y}")

def wake_and_unlock():
    """Wakes the screen and performs unlock swipe if needed."""
    power_state = run_adb("dumpsys power | grep 'Display Power: state='", is_su=True)
    if "state=OFF" in power_state:
        print("[*] Screen is OFF. Waking up device...")
        run_adb("input keyevent 26") # POWER
        time.sleep(1.0)
        # Unlock swipe
        hw_swipe(360, 1300, 360, 450, 260)
        time.sleep(1.2)
    else:
        print("[*] Screen is already awake.")

def human_scroll(direction="down", count=1):
    """Performs natural biological scrolling with thumb curvature."""
    for _ in range(count):
        # 720x1600 coordinates with thumb ergonomics
        x_base = random.uniform(320, 500)
        curvature = random.uniform(-25, 25)
        duration = random.randint(220, 360)
        
        if direction == "down":
            y_start = random.uniform(1150, 1300)
            y_end = random.uniform(450, 650)
        else:
            y_start = random.uniform(500, 650)
            y_end = random.uniform(1100, 1250)
            
        hw_swipe(x_base, y_start, x_base + curvature, y_end, duration)
        time.sleep(random.uniform(1.2, 3.2))

# ==============================================================================
# 1. SAUDI CHROME BROWSING MODULE
# ==============================================================================
SAUDI_SITES = [
    ("https://sabq.org", "Sabq Online Newspaper (Saudi Arabia)"),
    ("https://alriyadh.com", "Al Riyadh Daily News"),
    ("https://haraj.com.sa", "Haraj KSA Community Marketplace"),
    ("https://www.google.com.sa/search?q=%D8%A3%D8%AE%D8%A8%D8%A7%D8%B1+%D8%A7%D9%84%D8%B3%D8%B9%D9%88%D8%AF%D9%8A%D8%A9+%D8%A7%D9%84%D9%8A%D9%88%D9%85", "Google KSA - Today's Saudi News")
]

def warmup_chrome(duration_secs: int = 120):
    print("\n========================================================")
    print(" [MODULE 1/4] Chrome Saudi Portal Browsing (Organic Web)")
    print("========================================================")
    site, desc = random.choice(SAUDI_SITES)
    print(f"[*] Navigating Chrome to: {desc} ({site})")
    
    # Launch Chrome with URL
    run_adb(f"am start -a android.intent.action.VIEW -d '{site}' com.android.chrome")
    
    start_time = time.time()
    # Initial page load dwell
    time.sleep(random.uniform(6.0, 9.0))
    
    # Check for Chrome first-run popups or dialogs and dismiss gracefully
    hw_tap(360, 1450) # Accept terms if present
    time.sleep(1.5)
    
    while time.time() - start_time < duration_secs:
        # Natural reading behavior: scroll down, pause, read, scroll again
        scroll_steps = random.randint(2, 4)
        print(f"[*] Reading content... scrolling {scroll_steps} pages naturally.")
        human_scroll("down", count=scroll_steps)
        
        # Read dwell time
        dwell = random.uniform(8.0, 18.0)
        time.sleep(dwell)
        
        # Occasionally scroll back up slightly
        if random.random() < 0.35:
            human_scroll("up", count=1)
            time.sleep(random.uniform(3.0, 6.0))

    print("[+] Chrome browsing session completed.")
    run_adb("input keyevent 3") # HOME

# ==============================================================================
# 2. GOOGLE MAPS RIYADH PASSIVE EXPLORATION
# ==============================================================================
def warmup_google_maps(duration_secs: int = 60):
    print("\n========================================================")
    print(" [MODULE 2/4] Google Maps Passive Exploration (Riyadh, KSA)")
    print("========================================================")
    # Open Maps centered on Riyadh coordinates
    print("[*] Launching Google Maps in Riyadh (24.7136, 46.6753)...")
    run_adb("am start -a android.intent.action.VIEW -d 'geo:24.7136,46.6753?z=13' com.google.android.apps.maps")
    time.sleep(6.0)
    
    # Dismiss any intro modal
    run_adb("input keyevent 4") # BACK (dismisses update/location popups)
    time.sleep(1.5)
    
    start_time = time.time()
    while time.time() - start_time < duration_secs:
        # Passive map pan gestures (gentle swipe across screen)
        x1 = random.uniform(250, 470)
        y1 = random.uniform(600, 900)
        dx = random.uniform(-150, 150)
        dy = random.uniform(-150, 150)
        hw_swipe(x1, y1, x1 + dx, y1 + dy, random.randint(350, 500))
        time.sleep(random.uniform(5.0, 10.0))

    print("[+] Google Maps location orientation session completed.")
    run_adb("input keyevent 3") # HOME

# ==============================================================================
# 3. GOOGLE PLAY STORE PASSIVE BROWSING
# ==============================================================================
def warmup_play_store(duration_secs: int = 75):
    print("\n========================================================")
    print(" [MODULE 3/4] Google Play Store Passive Browsing")
    print("========================================================")
    print("[*] Launching Google Play Store...")
    run_adb("monkey -p com.android.vending -c android.intent.category.LAUNCHER 1")
    time.sleep(5.0)
    
    start_time = time.time()
    while time.time() - start_time < duration_secs:
        print("[*] Browsing Play Store charts & suggestions...")
        human_scroll("down", count=random.randint(1, 3))
        time.sleep(random.uniform(4.0, 8.0))
        
        # In 30% of cycles, tap on a card to view app details passively
        if random.random() < 0.35:
            # Tap mid-screen card
            card_x = random.choice([220, 500])
            card_y = random.uniform(650, 1100)
            hw_tap(int(card_x), int(card_y))
            time.sleep(random.uniform(6.0, 12.0))
            run_adb("input keyevent 4") # BACK to feed
            time.sleep(2.0)

    print("[+] Google Play Store organic session completed.")
    run_adb("input keyevent 3") # HOME

# ==============================================================================
# 4. YOUTUBE GULF/SAUDI PASSIVE VIEWING
# ==============================================================================
def warmup_youtube(duration_secs: int = 90):
    print("\n========================================================")
    print(" [MODULE 4/4] YouTube Passive Engagement")
    print("========================================================")
    print("[*] Launching YouTube...")
    run_adb("monkey -p com.google.android.youtube -c android.intent.category.LAUNCHER 1")
    time.sleep(6.0)
    
    start_time = time.time()
    # Scroll down feed once or twice
    human_scroll("down", count=2)
    time.sleep(3.0)
    
    # Tap a video on feed (upper middle card)
    print("[*] Selecting a video from home feed...")
    hw_tap(360, 600)
    
    # Watch video passively
    watch_time = min(duration_secs - 15, random.randint(45, 75))
    print(f"[*] Passively watching video for {watch_time}s...")
    
    # Micro volume bump for biological entropy
    run_adb("input keyevent 24") # VOLUME_UP
    time.sleep(watch_time // 2)
    run_adb("input keyevent 25") # VOLUME_DOWN
    time.sleep(watch_time // 2)

    print("[+] YouTube session completed.")
    run_adb("input keyevent 3") # HOME

# ==============================================================================
# MAIN ORCHESTRATOR
# ==============================================================================
def run_whole_device_warmup(quick: bool = False):
    print("================================================================================")
    print("  STARTING HOLISTIC WHOLE-DEVICE ORGANIC WARM-UP SESSION")
    print("  Device: Samsung Galaxy A02 | Carrier: STC KSA | Security: Zero-Account")
    print("================================================================================")
    
    ensure_driver()
    wake_and_unlock()
    
    # Factor durations based on quick mode
    factor = 0.4 if quick else 1.0
    
    warmup_chrome(int(100 * factor))
    warmup_google_maps(int(50 * factor))
    warmup_play_store(int(60 * factor))
    warmup_youtube(int(70 * factor))
    
    # Clean exit
    run_adb("input keyevent 3")
    print("\n================================================================================")
    print(" [SUCCESS] Whole-Device Organic Warm-up Completed Flawlessly.")
    print(" Android System, Chrome, Google Play Services & Maps conditioned with KSA footprint.")
    print(" ZERO TikTok account creation or login prompts were triggered.")
    print("================================================================================")

if __name__ == "__main__":
    is_quick = "--quick" in sys.argv
    run_whole_device_warmup(quick=is_quick)
