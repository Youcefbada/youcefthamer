#!/system/bin/sh
# ==============================================================================
# 95-singbox-tproxy.sh
# KSA TikTok Enterprise - Zero-Interface Transparent Proxy (TPROXY) Engine
# Eliminates tun0 completely so ByteDance MetaSec raw syscall probes see only wlan0!
# Target: Samsung Galaxy A02 (SM-A022F / Android 11 API 30 / Kernel 4.19 ARM32)
# ==============================================================================

BIN="/data/local/tmp/sing-box"
CONF="/data/local/tmp/singbox_config.json"
LOG="/data/local/tmp/singbox_tproxy.log"
TPROXY_PORT=12345
FWMARK=1
TABLE=100

start_tproxy() {
    echo "[*] Initializing Zero-Interface TPROXY Engine via sing-box..."

    if [ ! -f "$BIN" ]; then
        echo "[!] Error: sing-box binary not found at $BIN"
        exit 1
    fi

    # 1. Start sing-box daemon
    pkill -f "$BIN" 2>/dev/null
    nohup "$BIN" run -c "$CONF" > "$LOG" 2>&1 &
    sleep 2

    PID=$(pidof sing-box 2>/dev/null)
    if [ -z "$PID" ]; then
        echo "[!] Failed to start sing-box. Check $LOG"
        exit 1
    fi
    echo "[+] sing-box daemon active (PID $PID)"

    # 2. Configure Linux Policy Routing Table
    ip rule del fwmark $FWMARK table $TABLE 2>/dev/null
    ip route del local default dev lo table $TABLE 2>/dev/null

    ip rule add fwmark $FWMARK table $TABLE
    ip route add local default dev lo table $TABLE

    # 3. Configure iptables Mangle TPROXY Chains
    iptables -t mangle -D PREROUTING -j SINGBOX_TPROXY 2>/dev/null
    iptables -t mangle -D OUTPUT -j SINGBOX_OUTPUT 2>/dev/null
    iptables -t mangle -F SINGBOX_TPROXY 2>/dev/null
    iptables -t mangle -X SINGBOX_TPROXY 2>/dev/null
    iptables -t mangle -F SINGBOX_OUTPUT 2>/dev/null
    iptables -t mangle -X SINGBOX_OUTPUT 2>/dev/null

    # PREROUTING
    iptables -t mangle -N SINGBOX_TPROXY
    iptables -t mangle -A SINGBOX_TPROXY -d 0.0.0.0/8 -j RETURN
    iptables -t mangle -A SINGBOX_TPROXY -d 10.0.0.0/8 -j RETURN
    iptables -t mangle -A SINGBOX_TPROXY -d 127.0.0.0/8 -j RETURN
    iptables -t mangle -A SINGBOX_TPROXY -d 169.254.0.0/16 -j RETURN
    iptables -t mangle -A SINGBOX_TPROXY -d 172.16.0.0/12 -j RETURN
    iptables -t mangle -A SINGBOX_TPROXY -d 192.168.0.0/16 -j RETURN
    iptables -t mangle -A SINGBOX_TPROXY -d 224.0.0.0/4 -j RETURN
    iptables -t mangle -A SINGBOX_TPROXY -d 240.0.0.0/4 -j RETURN
    iptables -t mangle -A SINGBOX_TPROXY -p tcp -j TPROXY --on-port $TPROXY_PORT --tproxy-mark $FWMARK
    iptables -t mangle -A SINGBOX_TPROXY -p udp -j TPROXY --on-port $TPROXY_PORT --tproxy-mark $FWMARK
    iptables -t mangle -A PREROUTING -j SINGBOX_TPROXY

    # OUTPUT (local Android apps)
    iptables -t mangle -N SINGBOX_OUTPUT
    iptables -t mangle -A SINGBOX_OUTPUT -m owner --uid-owner 0 -j RETURN # Avoid sing-box loop
    iptables -t mangle -A SINGBOX_OUTPUT -d 0.0.0.0/8 -j RETURN
    iptables -t mangle -A SINGBOX_OUTPUT -d 10.0.0.0/8 -j RETURN
    iptables -t mangle -A SINGBOX_OUTPUT -d 127.0.0.0/8 -j RETURN
    iptables -t mangle -A SINGBOX_OUTPUT -d 169.254.0.0/16 -j RETURN
    iptables -t mangle -A SINGBOX_OUTPUT -d 172.16.0.0/12 -j RETURN
    iptables -t mangle -A SINGBOX_OUTPUT -d 192.168.0.0/16 -j RETURN
    iptables -t mangle -A SINGBOX_OUTPUT -d 224.0.0.0/4 -j RETURN
    iptables -t mangle -A SINGBOX_OUTPUT -d 240.0.0.0/4 -j RETURN
    iptables -t mangle -A SINGBOX_OUTPUT -p tcp -j MARK --set-mark $FWMARK
    iptables -t mangle -A SINGBOX_OUTPUT -p udp -j MARK --set-mark $FWMARK
    iptables -t mangle -A OUTPUT -j SINGBOX_OUTPUT

    echo "[SUCCESS] Zero-Interface TPROXY Active! ZERO tun/ppp interfaces created."
}

stop_tproxy() {
    echo "[*] Tearing down TPROXY rules and stopping sing-box..."
    pkill -f "$BIN" 2>/dev/null

    iptables -t mangle -D PREROUTING -j SINGBOX_TPROXY 2>/dev/null
    iptables -t mangle -D OUTPUT -j SINGBOX_OUTPUT 2>/dev/null
    iptables -t mangle -F SINGBOX_TPROXY 2>/dev/null
    iptables -t mangle -X SINGBOX_TPROXY 2>/dev/null
    iptables -t mangle -F SINGBOX_OUTPUT 2>/dev/null
    iptables -t mangle -X SINGBOX_OUTPUT 2>/dev/null

    ip rule del fwmark $FWMARK table $TABLE 2>/dev/null
    ip route del local default dev lo table $TABLE 2>/dev/null
    echo "[+] TPROXY successfully stopped. Clean state restored."
}

status_tproxy() {
    PID=$(pidof sing-box 2>/dev/null)
    echo "========================================================"
    echo "       ZERO-INTERFACE TPROXY STATUS (sing-box)"
    echo "========================================================"
    if [ -n "$PID" ]; then
        echo "[*] sing-box Engine : [ACTIVE - PID $PID]"
    else
        echo "[*] sing-box Engine : [STOPPED]"
    fi

    # Check for any active VPN TUN/PPP interface (e.g. tun0, ppp0)
    TUN_COUNT=$(ip link show | grep -E '^\s*[0-9]+:\s*(tun[0-9]|ppp[0-9])' | wc -l)
    if [ "$TUN_COUNT" -eq 0 ]; then
        echo "[*] TUN Interface   : [ZERO TUN - INVISIBLE TO METASEC RAW SYSCALLS]"
    else
        echo "[!] TUN Interface   : [WARNING - $TUN_COUNT ACTIVE TUN/PPP INTERFACE DETECTED]"
    fi

    RULE_ACTIVE=$(iptables -t mangle -L SINGBOX_TPROXY 2>/dev/null | grep -c TPROXY)
    echo "[*] TPROXY iptables : $RULE_ACTIVE active interception rules"
    echo "========================================================"
}

case "$1" in
    start)
        start_tproxy
        ;;
    stop)
        stop_tproxy
        ;;
    status)
        status_tproxy
        ;;
    restart)
        stop_tproxy
        sleep 1
        start_tproxy
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        exit 1
        ;;
esac
