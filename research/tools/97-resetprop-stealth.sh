#!/system/bin/sh
# 97-resetprop-stealth.sh
# Native bootloader property sanitization for ByteDance / libmetasec_ml.so raw /dev/__properties__ readers

while [ "$(getprop sys.boot_completed)" != "1" ]; do
    sleep 2
done

resetprop -n ro.boot.verifiedbootstate green
resetprop -n ro.boot.flash.locked 1
resetprop -n ro.boot.vbmeta.device_state locked
resetprop -n ro.boot.warranty_bit 0
resetprop -n ro.warranty_bit 0
resetprop -n ro.debuggable 0
resetprop -n ro.secure 1
resetprop -n ro.build.type user
resetprop -n ro.build.tags release-keys
resetprop -n sys.usb.state mtp
resetprop -n sys.usb.config mtp
resetprop -n init.svc.adbd stopped
