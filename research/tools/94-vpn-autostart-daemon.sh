#!/system/bin/sh
# ==============================================================================
# 94-vpn-autostart-daemon.sh
# KSA TikTok Enterprise - Automated Saudi VPN Autostart & Reconnection Watchdog
# Target: Samsung Galaxy A02 (SM-A022F / Android 11 API 30 / Magisk Root)
# ==============================================================================

LOGFILE="/data/local/tmp/vpn_autostart.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting VPN Autostart & Watchdog Daemon..." >> "$LOGFILE"

# 1. Wait for Android system boot completion
while [ "$(getprop sys.boot_completed)" != "1" ]; do
    sleep 2
done

# 2. Configure Android Always-On VPN system settings
settings put secure always_on_vpn_app com.urbanvpn.android 2>/dev/null

# Function: Pin OOM score to -900 (Immunity against Android Low-Memory Killer)
pin_oom() {
    for pkg in com.urbanvpn.android libpie_openvpn com.v2ray.ang; do
        for p in $(pgrep -f "$pkg" 2>/dev/null); do
            if [ -d "/proc/$p" ]; then
                echo -900 > /proc/$p/oom_score_adj 2>/dev/null
            fi
        done
    done
}

# Function: Connect Urban VPN automatically
connect_vpn() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [RECONNECT] Triggering Urban VPN automatic connection..." >> "$LOGFILE"

    # Check if screen is off; if so, wake it up temporarily
    SCREEN_STATE=$(dumpsys power 2>/dev/null | grep -i 'mWakefulness=' | head -n 1)
    WAS_ASLEEP=0
    if echo "$SCREEN_STATE" | grep -qi 'Asleep'; then
        WAS_ASLEEP=1
        input keyevent 224 # KEYCODE_WAKEUP
        sleep 1
    fi
    wm dismiss-keyguard 2>/dev/null

    # Launch Urban VPN via launcher intent
    monkey -p com.urbanvpn.android -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1
    sleep 2

    # Dismiss any "Skip" or permission prompt if displayed (coordinates 187, 1427)
    input tap 187 1427 2>/dev/null
    sleep 1

    # Tap Connect button on Saudi Arabia profile (coordinates 359, 526)
    input tap 359 526 2>/dev/null

    # Wait up to 15 seconds for tun0 interface to come UP
    for i in $(seq 1 15); do
        if ip link show tun0 2>/dev/null | grep -q "UP"; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS] tun0 is UP!" >> "$LOGFILE"
            break
        fi
        sleep 1
    done

    # Neatly return to Home screen so VPN app stays in background
    input keyevent 3 # KEYCODE_HOME

    # Protect new processes immediately
    pin_oom

    # If screen was asleep before connection, turn it back off
    if [ "$WAS_ASLEEP" = "1" ]; then
        input keyevent 223 # KEYCODE_SLEEP
    fi
}

# 3. Main Persistent Watchdog Loop
FAIL_COUNT=0

while true; do
    # Check if Wi-Fi (wlan0) is connected
    WLAN_UP=$(ip link show wlan0 2>/dev/null | grep -q "UP" && echo 1 || echo 0)

    if [ "$WLAN_UP" = "1" ]; then
        # Check if tun0 is active
        TUN_UP=$(ip link show tun0 2>/dev/null | grep -q "UP" && echo 1 || echo 0)

        if [ "$TUN_UP" != "1" ]; then
            FAIL_COUNT=$((FAIL_COUNT + 1))
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ALERT] tun0 is DOWN (fail_count=$FAIL_COUNT). Reconnecting..." >> "$LOGFILE"
            connect_vpn
            sleep 5
        else
            FAIL_COUNT=0
            # Keep pinning OOM score to prevent kill during background execution
            pin_oom
        fi
    fi

    # Poll every 5 seconds
    sleep 5
done
