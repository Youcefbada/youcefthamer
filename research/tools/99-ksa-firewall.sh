#!/system/bin/sh
# 99-ksa-firewall.sh
# Hardened Zero-Leak Kernel Firewall for KSA TikTok Enterprise Node
# Eliminates IPv6, QUIC UDP 443, and WebRTC STUN/UDP leaks over physical interfaces

# 1. Total IPv6 Blackhole at Kernel Level
ip6tables -P OUTPUT DROP 2>/dev/null
ip6tables -P FORWARD DROP 2>/dev/null
ip6tables -P INPUT DROP 2>/dev/null
sysctl -w net.ipv6.conf.all.disable_ipv6=1 2>/dev/null
sysctl -w net.ipv6.conf.default.disable_ipv6=1 2>/dev/null
sysctl -w net.ipv6.conf.wlan0.disable_ipv6=1 2>/dev/null

# 2. Flush any previous custom rules in our chains to prevent duplicates
iptables -D OUTPUT -p udp --dport 443 -j REJECT 2>/dev/null
iptables -D OUTPUT -o wlan0 -m owner --uid-owner 10205 -j REJECT 2>/dev/null
iptables -D OUTPUT -o wlan0 -p udp -m owner --uid-owner 10205 -j REJECT 2>/dev/null

# 3. Intercept QUIC UDP 443 universally to force TCP TLS 1.3 fallback for SSCronet
iptables -I OUTPUT -p udp --dport 443 -j REJECT

# 4. Strict WebRTC & Direct Physical Socket Leak Protection:
# TikTok (UID 10205) must route exclusively through the encrypted tunnel (tun0).
# Any UDP packets (STUN, WebRTC, direct probes) attempting to escape directly via wlan0 are rejected.
iptables -I OUTPUT -o wlan0 -p udp -m owner --uid-owner 10205 -j REJECT
