#!/system/bin/sh
cp /data/local/tmp/99-ksa-firewall.sh /data/adb/service.d/
cp /data/local/tmp/98-vpn-oom-guard.sh /data/adb/service.d/
chmod 755 /data/adb/service.d/99-ksa-firewall.sh
chmod 755 /data/adb/service.d/98-vpn-oom-guard.sh
sh /data/adb/service.d/99-ksa-firewall.sh
sh /data/adb/service.d/98-vpn-oom-guard.sh
settings put global window_animation_scale 0.5
settings put global transition_animation_scale 0.5
settings put global animator_duration_scale 0.5
sysctl -w vm.swappiness=100
sysctl -w vm.vfs_cache_pressure=50
pm disable-user --user 0 com.samsung.android.mds 2>/dev/null
pm disable-user --user 0 com.sec.spp.push 2>/dev/null
pm disable-user --user 0 com.samsung.android.game.gamehome 2>/dev/null
echo "SERVICES_INSTALLED_SUCCESSFULLY"
