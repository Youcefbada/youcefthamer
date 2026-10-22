package io.github.meiyongai.toki.hook

import android.content.Context
import android.net.wifi.ScanResult
import android.net.wifi.WifiInfo
import android.net.wifi.WifiManager
import android.os.SystemClock
import android.telephony.CellInfo
import android.telephony.CellInfoLte
import android.telephony.SubscriptionInfo
import android.telephony.TelephonyManager
import android.telephony.gsm.GsmCellLocation
import android.util.Log
import io.github.meiyongai.toki.model.RegionPresets
import io.github.meiyongai.toki.provider.ConfigClient
import io.github.libxposed.api.XposedModule
import java.lang.reflect.Modifier

/**
 * 运营商与 SIM 卡地域伪装信息数据载荷。
 *
 * @property countryIso 两位 ISO 3166-1 国家或地区代号（全小写）。
 * @property operatorCode 移动国家代码（MCC）与移动网络代码（MNC）组合。
 * @property operatorName 运营商官方显示名称。
 */
data class CarrierInfo(
    val countryIso: String,
    val operatorCode: String,
    val operatorName: String
)

/**
 * SIM 卡与运营商地域伪装 Hook 核心处理器（TokiSimHook v2.0 Enterprise）。
 *
 * 拦截目标应用进程内对 [TelephonyManager]、[SubscriptionInfo]、[WifiManager] 以及基站信息 [CellInfoLte] 的各项反射及 JNI 调用，
 * 将 SIM 卡国家代码、运营商代号、基站蜂窝信息、Wi-Fi BSSID/SSID 重定向至沙特 STC 真实网络环境。
 */
object SimHook {

    private const val TAG = "TokiSimHook"

    /** 功能总开关状态，默认为开启 */
    @Volatile
    private var isEnabled: Boolean = true

    /** 当前运行时的运营商伪装数据载荷，默认预置沙特 STC */
    @Volatile
    private var activeCarrier: CarrierInfo = CarrierInfo(
        countryIso = "sa",
        operatorCode = "42001",
        operatorName = "STC"
    )

    /** 真实沙特电信 (STC) 光纤路由器 BSSID 与 SSID */
    private const val STC_FIBER_BSSID = "48:fd:8e:b1:2c:4d"
    private const val STC_FIBER_SSID = "\"STC_5G_Home_A8F\""

    fun resolveCarrier(
        regionCode: String,
        customOperatorCode: String?,
        customOperatorName: String?
    ): CarrierInfo {
        val normalizedIso = regionCode.trim().lowercase()
        val preset = RegionPresets.findByIso(normalizedIso)

        val finalOperatorCode = if (!customOperatorCode.isNullOrBlank()) {
            customOperatorCode.trim()
        } else {
            preset?.operatorCode ?: "00000"
        }

        val finalOperatorName = if (!customOperatorName.isNullOrBlank()) {
            customOperatorName.trim()
        } else {
            preset?.operatorName ?: "${normalizedIso.uppercase()} Carrier"
        }

        return CarrierInfo(
            countryIso = normalizedIso,
            operatorCode = finalOperatorCode,
            operatorName = finalOperatorName
        )
    }

    fun refreshConfig(context: Context) {
        isEnabled = ConfigClient.getBoolean(context, "sim_spoof_enabled")
        if (!isEnabled) {
            Log.i(TAG, "SIM 卡与地域伪装功能处于关闭状态")
            return
        }

        val targetRegion = ConfigClient.getString(context, "target_region", defaultValue = "SA") ?: "SA"
        val customOpCode = ConfigClient.getString(context, "sim_operator_code", defaultValue = null)
        val customOpName = ConfigClient.getString(context, "sim_operator_name", defaultValue = null)

        activeCarrier = resolveCarrier(targetRegion, customOpCode, customOpName)
        Log.i(
            TAG,
            "已同步目标国家/地区配置 -> ${activeCarrier.countryIso.uppercase()} | ${activeCarrier.operatorName} (${activeCarrier.operatorCode})"
        )
    }

    fun getActiveCarrier(): CarrierInfo = activeCarrier

    fun isFeatureEnabled(): Boolean = isEnabled

    /**
     * 构造沙特利雅得 STC LTE 蜂窝基站数据。
     */
    private fun createSaudiCellLocation(): GsmCellLocation {
        val loc = GsmCellLocation()
        loc.setLacAndCid(14102, 28491021)
        try {
            val pscField = GsmCellLocation::class.java.getDeclaredField("mPsc")
            pscField.isAccessible = true
            pscField.setInt(loc, 184)
        } catch (_: Throwable) {}
        return loc
    }

    private fun createSaudiCellInfo(): List<CellInfo> {
        return try {
            val cellInfoClass = Class.forName("android.telephony.CellInfoLte")
            val constructor = cellInfoClass.getDeclaredConstructor()
            constructor.isAccessible = true
            val cellInfo = constructor.newInstance() as CellInfo
            listOf(cellInfo)
        } catch (t: Throwable) {
            Log.w(TAG, "CellInfoLte 实例化异常: ${t.message}")
            emptyList()
        }
    }

    /**
     * 构造沙特利雅得 4 个周边 Wi-Fi 路由器的扫描结果，消除空扫描列表红线。
     */
    private fun createSaudiScanResults(): List<ScanResult> {
        return try {
            val nowMicros = SystemClock.elapsedRealtime() * 1000
            val ap1 = ScanResult().apply {
                SSID = "STC_5G_Home_A8F"
                BSSID = "48:fd:8e:b1:2c:4d"
                capabilities = "[WPA2-PSK-CCMP][RSN-PSK-CCMP][ESS]"
                level = -51
                frequency = 5180
                timestamp = nowMicros
            }
            val ap2 = ScanResult().apply {
                SSID = "STC_Fiber_5GHz"
                BSSID = "88:28:b3:7f:a2:10"
                capabilities = "[WPA2-PSK-CCMP][RSN-PSK-CCMP][ESS]"
                level = -64
                frequency = 5220
                timestamp = nowMicros - 4000
            }
            val ap3 = ScanResult().apply {
                SSID = "Mobily_Fiber_92B"
                BSSID = "c8:d1:5e:33:12:88"
                capabilities = "[WPA2-PSK-CCMP][RSN-PSK-CCMP][ESS]"
                level = -72
                frequency = 2437
                timestamp = nowMicros - 12000
            }
            val ap4 = ScanResult().apply {
                SSID = "Zain_Home_4G"
                BSSID = "00:1e:10:bc:90:3f"
                capabilities = "[WPA2-PSK-CCMP][RSN-PSK-CCMP][ESS]"
                level = -79
                frequency = 2412
                timestamp = nowMicros - 18000
            }
            listOf(ap1, ap2, ap3, ap4)
        } catch (t: Throwable) {
            Log.w(TAG, "ScanResult 构造异常: ${t.message}")
            emptyList()
        }
    }

    private fun hookTelephonyManager(module: XposedModule) {
        val telephonyClass = TelephonyManager::class.java
        for (method in telephonyClass.declaredMethods) {
            if (Modifier.isAbstract(method.modifiers)) continue

            when (method.name) {
                "getSimCountryIso", "getNetworkCountryIso" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) getActiveCarrier().countryIso else chain.proceed()
                    }
                }
                "getSimOperator", "getNetworkOperator" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) getActiveCarrier().operatorCode else chain.proceed()
                    }
                }
                "getSimOperatorName", "getNetworkOperatorName" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) getActiveCarrier().operatorName else chain.proceed()
                    }
                }
                "getSimState" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) TelephonyManager.SIM_STATE_READY else chain.proceed()
                    }
                }
                "hasIccCard" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) true else chain.proceed()
                    }
                }
                "getPhoneType" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) TelephonyManager.PHONE_TYPE_GSM else chain.proceed()
                    }
                }
                "getAllCellInfo" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) createSaudiCellInfo() else chain.proceed()
                    }
                }
                "getCellLocation" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) createSaudiCellLocation() else chain.proceed()
                    }
                }
                "getSubscriberId" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) getActiveCarrier().operatorCode + "0123456789" else chain.proceed()
                    }
                }
                "getSimSerialNumber" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) "89966" + getActiveCarrier().operatorCode + "12345678" else chain.proceed()
                    }
                }
                "getLine1Number" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) "+966501234567" else chain.proceed()
                    }
                }
            }
        }
        Log.i(TAG, "TelephonyManager 相关方法 Hook 拦截器注册完成")
    }

    private fun hookSubscriptionInfo(module: XposedModule) {
        val subInfoClass = SubscriptionInfo::class.java
        for (method in subInfoClass.declaredMethods) {
            if (Modifier.isAbstract(method.modifiers)) continue
            when (method.name) {
                "getCountryIso" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) getActiveCarrier().countryIso else chain.proceed()
                    }
                }
                "getMccString" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) getActiveCarrier().operatorCode.take(3) else chain.proceed()
                    }
                }
                "getMncString" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) getActiveCarrier().operatorCode.drop(3) else chain.proceed()
                    }
                }
                "getMcc" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) getActiveCarrier().operatorCode.take(3).toIntOrNull() ?: 420 else chain.proceed()
                    }
                }
                "getMnc" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) getActiveCarrier().operatorCode.drop(3).toIntOrNull() ?: 1 else chain.proceed()
                    }
                }
                "getCarrierName", "getDisplayName" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) getActiveCarrier().operatorName else chain.proceed()
                    }
                }
            }
        }
        Log.i(TAG, "SubscriptionInfo 相关方法 Hook 拦截器注册完成")
    }

    /**
     * 拦截 CellIdentityLte 与 CellSignalStrengthLte，提供真实的沙特 STC 蜂窝指标。
     */
    private fun hookCellInfoClasses(module: XposedModule) {
        try {
            val cellInfoLteClass = Class.forName("android.telephony.CellInfoLte")
            for (method in cellInfoLteClass.declaredMethods) {
                if (Modifier.isAbstract(method.modifiers)) continue
                if (method.name == "isRegistered") {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) true else chain.proceed()
                    }
                }
            }

            val cellIdentityLteClass = Class.forName("android.telephony.CellIdentityLte")
            for (method in cellIdentityLteClass.declaredMethods) {
                if (Modifier.isAbstract(method.modifiers)) continue
                when (method.name) {
                    "getMccString" -> module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) "420" else chain.proceed()
                    }
                    "getMncString" -> module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) "01" else chain.proceed()
                    }
                    "getMcc" -> module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) 420 else chain.proceed()
                    }
                    "getMnc" -> module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) 1 else chain.proceed()
                    }
                    "getTac" -> module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) 14102 else chain.proceed()
                    }
                    "getCi" -> module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) 28491021 else chain.proceed()
                    }
                    "getPci" -> module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) 184 else chain.proceed()
                    }
                    "getEarfcn" -> module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) 1650 else chain.proceed()
                    }
                    "getMobileNetworkOperator" -> module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) "42001" else chain.proceed()
                    }
                    "getOperatorAlphaLong", "getOperatorAlphaShort" -> module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) "STC" else chain.proceed()
                    }
                    "getBands" -> module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) intArrayOf(3) else chain.proceed()
                    }
                }
            }

            val signalStrengthLteClass = Class.forName("android.telephony.CellSignalStrengthLte")
            for (method in signalStrengthLteClass.declaredMethods) {
                if (Modifier.isAbstract(method.modifiers)) continue
                when (method.name) {
                    "getDbm", "getRsrp" -> module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) -85 else chain.proceed()
                    }
                    "getRsrq" -> module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) -9 else chain.proceed()
                    }
                    "getRssnr" -> module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) 15 else chain.proceed()
                    }
                    "getLevel" -> module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) 4 else chain.proceed()
                    }
                    "getAsuLevel" -> module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) 55 else chain.proceed()
                    }
                }
            }
            Log.i(TAG, "CellIdentityLte 与 CellSignalStrengthLte 基站拦截器注册完成")
        } catch (t: Throwable) {
            Log.w(TAG, "hookCellInfoClasses 注册异常: ${t.message}")
        }
    }

    /**
     * 拦截 WifiManager 扫描结果及 WifiInfo，消除 02:00:00:00:00:00 异常 BSSID。
     */
    private fun hookWifi(module: XposedModule) {
        val wifiClass = WifiManager::class.java
        for (method in wifiClass.declaredMethods) {
            if (Modifier.isAbstract(method.modifiers)) continue
            when (method.name) {
                "getScanResults" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) createSaudiScanResults() else chain.proceed()
                    }
                }
                "getCountryCode" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) getActiveCarrier().countryIso.uppercase() else chain.proceed()
                    }
                }
            }
        }

        val wifiInfoClass = WifiInfo::class.java
        for (method in wifiInfoClass.declaredMethods) {
            if (Modifier.isAbstract(method.modifiers)) continue
            when (method.name) {
                "getBSSID" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) STC_FIBER_BSSID else chain.proceed()
                    }
                }
                "getSSID" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) STC_FIBER_SSID else chain.proceed()
                    }
                }
                "getNetworkId" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) 1 else chain.proceed()
                    }
                }
                "getLinkSpeed" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) 433 else chain.proceed()
                    }
                }
                "getFrequency" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) 5180 else chain.proceed()
                    }
                }
                "getRssi" -> {
                    module.trackHook("SimHook", method).intercept { chain ->
                        if (isFeatureEnabled()) {
                            val jitter = ((SystemClock.elapsedRealtime() / 1500) % 5).toInt() - 2
                            -52 + jitter
                        } else {
                            chain.proceed()
                        }
                    }
                }
            }
        }
        Log.i(TAG, "WifiManager 与 WifiInfo 真实沙特光纤路由拦截器注册完成")
    }

    fun init(module: XposedModule) {
        hookTelephonyManager(module)
        hookSubscriptionInfo(module)
        hookCellInfoClasses(module)
        hookWifi(module)
        Log.i(TAG, "SIM 卡与沙特蜂窝/Wi-Fi 地域伪装子系统就绪")
    }
}
