#!/system/bin/sh
# ================================================================================
# 96-singbox-watchdog.sh - Zero-Interface TPROXY Watchdog Daemon
# Monitors sing-box process and restarts it if crashed or OOM-killed.
# Deploy to /data/adb/service.d/ for automatic boot execution.
# ================================================================================

SINGBOX_BIN="/data/local/tmp/sing-box"
SINGBOX_CONFIG="/data/local/tmp/singbox_config.json"
TPROXY_SCRIPT="/data/local/tmp/95-singbox-tproxy.sh"
LOG="/data/local/tmp/singbox_watchdog.log"
CHECK_INTERVAL=30
MAX_RESTARTS=10
RESTART_COUNT=0

echo "[$(date)] sing-box watchdog daemon started (interval=${CHECK_INTERVAL}s, max_restarts=${MAX_RESTARTS})" >> "$LOG"

while true; do
    if ! pidof sing-box > /dev/null 2>&1; then
        RESTART_COUNT=$((RESTART_COUNT + 1))
        if [ "$RESTART_COUNT" -gt "$MAX_RESTARTS" ]; then
            echo "[$(date)] CRITICAL: Exceeded max restart attempts (${MAX_RESTARTS}). Watchdog halting." >> "$LOG"
            exit 1
        fi

        echo "[$(date)] sing-box not running! Restart attempt ${RESTART_COUNT}/${MAX_RESTARTS}..." >> "$LOG"

        if [ -x "$TPROXY_SCRIPT" ]; then
            "$TPROXY_SCRIPT" start >> "$LOG" 2>&1
        elif [ -x "$SINGBOX_BIN" ]; then
            nohup "$SINGBOX_BIN" run -c "$SINGBOX_CONFIG" >> "$LOG" 2>&1 &
        else
            echo "[$(date)] ERROR: Neither TPROXY script nor sing-box binary found!" >> "$LOG"
        fi

        sleep 5

        if pidof sing-box > /dev/null 2>&1; then
            echo "[$(date)] sing-box restarted successfully (PID: $(pidof sing-box))" >> "$LOG"
            # Reset counter on successful restart
            RESTART_COUNT=0
        else
            echo "[$(date)] WARNING: sing-box failed to restart on attempt ${RESTART_COUNT}" >> "$LOG"
        fi
    fi
    sleep "$CHECK_INTERVAL"
done
