#!/system/bin/sh
# 98-vpn-oom-guard.sh
# Low-RAM MT6739 Performance & OOM Protection Service

# 1. Virtual Memory (VM) Optimization for eMMC 5.1 & ZRAM
sysctl -w vm.swappiness=100 2>/dev/null
sysctl -w vm.page-cluster=0 2>/dev/null
sysctl -w vm.vfs_cache_pressure=60 2>/dev/null
sysctl -w vm.dirty_background_ratio=5 2>/dev/null
sysctl -w vm.dirty_ratio=15 2>/dev/null
sysctl -w vm.min_free_kbytes=16384 2>/dev/null
sysctl -w vm.extra_free_kbytes=24576 2>/dev/null

# 2. Continuous OOM Score Guardian for Proxy Engine
while true; do
    PIDS=$(pgrep -f "com.v2ray.ang" 2>/dev/null)
    for p in $PIDS; do
        if [ -d "/proc/$p" ]; then
            echo -900 > /proc/$p/oom_score_adj 2>/dev/null
        fi
    done
    sleep 10
done &
