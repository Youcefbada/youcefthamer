#!/system/bin/sh
# 95-zero-interface-redirect.sh
# Zero-Interface Transparent NAT REDIRECT Architecture for TikTok (UID 10205)
# Eliminates tun0/ppp0 entirely from the kernel, blinding AF_NETLINK RTM_GETLINK scans.

TARGET_UID="10205"
PROXY_UID="9999"
TCP_REDIR_PORT="10810"
DNS_REDIR_PORT="10853"

# 1. Flush existing custom rules in OUTPUT chains
iptables -t nat -D OUTPUT -m owner --uid-owner $PROXY_UID -j RETURN 2>/dev/null
iptables -t nat -D OUTPUT -m owner --uid-owner $TARGET_UID -o lo -j RETURN 2>/dev/null
iptables -t nat -D OUTPUT -p udp -m owner --uid-owner $TARGET_UID --dport 53 -j REDIRECT --to-ports $DNS_REDIR_PORT 2>/dev/null
iptables -t nat -D OUTPUT -p tcp -m owner --uid-owner $TARGET_UID --dport 53 -j REDIRECT --to-ports $DNS_REDIR_PORT 2>/dev/null
iptables -t nat -D OUTPUT -p tcp -m owner --uid-owner $TARGET_UID -j REDIRECT --to-ports $TCP_REDIR_PORT 2>/dev/null

# 2. IPv6 Blackhole for Target UID
ip6tables -t filter -I OUTPUT 1 -m owner --uid-owner $TARGET_UID -j REJECT --reject-with icmp6-adm-prohibited 2>/dev/null

# 3. NAT OUTPUT Chain: Transparently redirect Target UID traffic
# Exclude traffic originating from Proxy Daemon (UID 9999)
iptables -t nat -A OUTPUT -m owner --uid-owner $PROXY_UID -j RETURN

# Allow local loopback traffic for target UID
iptables -t nat -A OUTPUT -m owner --uid-owner $TARGET_UID -o lo -j RETURN

# Redirect all DNS queries (UDP/TCP 53) from Target UID to proxy's DNS dokodemo-door port
iptables -t nat -A OUTPUT -p udp -m owner --uid-owner $TARGET_UID --dport 53 -j REDIRECT --to-ports $DNS_REDIR_PORT
iptables -t nat -A OUTPUT -p tcp -m owner --uid-owner $TARGET_UID --dport 53 -j REDIRECT --to-ports $DNS_REDIR_PORT

# Redirect all outbound TCP traffic from Target UID to proxy's TCP dokodemo-door port
iptables -t nat -A OUTPUT -p tcp -m owner --uid-owner $TARGET_UID -j REDIRECT --to-ports $TCP_REDIR_PORT

# 4. FILTER OUTPUT Chain: Fail-Closed Killswitch & Instant QUIC Rejection
iptables -t filter -I OUTPUT 1 -o lo -m owner --uid-owner $TARGET_UID -j ACCEPT 2>/dev/null
iptables -t filter -I OUTPUT 2 -p udp --dport 443 -m owner --uid-owner $TARGET_UID -j REJECT --reject-with icmp-port-unreachable 2>/dev/null
iptables -t filter -I OUTPUT 3 -m owner --uid-owner $TARGET_UID -j REJECT --reject-with icmp-net-unreachable 2>/dev/null
