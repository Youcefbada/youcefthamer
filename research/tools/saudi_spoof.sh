#!/system/bin/sh
# Wait for Android boot completion
while [ "$(getprop sys.boot_completed)" != "1" ]; do
    sleep 2
done

# Function to enforce Saudi Arabia identity
apply_saudi_identity() {
    # 1. Telephony & Cellular Network Identity (STC Saudi Arabia)
    resetprop -n gsm.operator.alpha "STC"
    resetprop -n gsm.operator.iso-country "sa"
    resetprop -n gsm.operator.numeric "42001"
    resetprop -n gsm.sim.operator.alpha "STC"
    resetprop -n gsm.sim.operator.iso-country "sa"
    resetprop -n gsm.sim.operator.numeric "42001"

    # 2. Samsung Regional CSC & Sales Code (Saudi Arabia Open - KSA)
    resetprop -n ro.csc.country_code "KSA"
    resetprop -n ro.csc.countryiso_code "SA"
    resetprop -n ro.csc.sales_code "KSA"
    resetprop -n ro.csc.omcnw_code "KSA"
    resetprop -n ro.csc.omcnw_code2 "KSA"
    resetprop -n ril.sales_code "KSA"

    # 3. System Timezone
    setprop persist.sys.timezone "Asia/Riyadh"

    # 4. Disable background Wi-Fi and Bluetooth scanning globally
    settings put global wifi_scan_always_enabled 0
    settings put global ble_scan_always_enabled 0
}

# Apply once immediately
apply_saudi_identity

# Start background persistent enforcement daemon
(
    while true; do
        sleep 10
        if [ "$(getprop gsm.operator.numeric)" != "42001" ]; then
            apply_saudi_identity
        fi
    done
) &

