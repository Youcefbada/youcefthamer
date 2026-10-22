package io.github.meiyongai.toki.hook

import android.content.Context
import android.location.Location
import android.location.LocationManager
import android.os.SystemClock
import android.util.Log
import io.github.meiyongai.toki.model.RegionPresets
import io.github.meiyongai.toki.provider.ConfigClient
import io.github.libxposed.api.XposedModule
import java.lang.reflect.Modifier
import java.util.concurrent.ThreadLocalRandom

/**
 * 系统 GPS 与地理位置（Location）微抖动拟真 Hook 核心处理器（TokiGpsHook v2.0 Enterprise）。
 *
 * 拦截目标应用对 [Location] 以及 [LocationManager] 的定位获取逻辑，
 * 将经纬度坐标重定向至沙特利雅得基准坐标 (24.7136, 46.6753)，
 * 注入高斯微漂移（±0.00005°）、拟真利雅得海拔（612m ± 1.5m）、动态精度与微速，
 * 彻底清除 [Location.isFromMockProvider] 虚拟定位标记，消除死板静态坐标的机刷/风控异常。
 */
object GpsHook {

    private const val TAG = "TokiGpsHook"

    @Volatile
    private var isEnabled: Boolean = true

    /** 沙特利雅得基准纬度 */
    @Volatile
    private var activeLatitude: Double = 24.7136

    /** 沙特利雅得基准经度 */
    @Volatile
    private var activeLongitude: Double = 46.6753

    /** 利雅得平均海拔 (米) */
    private const val BASE_ALTITUDE = 612.0

    fun refreshConfig(context: Context) {
        isEnabled = ConfigClient.getBoolean(context, "gps_spoof_enabled")
        if (!isEnabled) {
            Log.i(TAG, "系统 GPS 伪装功能处于关闭状态")
            return
        }

        val followRegion = ConfigClient.getBoolean(context, "gps_follow_region")
        if (followRegion) {
            val targetRegion = ConfigClient.getString(context, "target_region", defaultValue = "SA") ?: "SA"
            activeLatitude = RegionPresets.resolveLatitudeForIso(targetRegion)
            activeLongitude = RegionPresets.resolveLongitudeForIso(targetRegion)
        } else {
            val customLatStr = ConfigClient.getString(context, "custom_latitude", defaultValue = "24.7136") ?: "24.7136"
            val customLngStr = ConfigClient.getString(context, "custom_longitude", defaultValue = "46.6753") ?: "46.6753"
            activeLatitude = customLatStr.toDoubleOrNull() ?: 24.7136
            activeLongitude = customLngStr.toDoubleOrNull() ?: 46.6753
        }

        Log.i(TAG, "已同步伪装 GPS 坐标 -> ($activeLatitude, $activeLongitude) (followRegion=$followRegion)")
    }

    fun isFeatureEnabled(): Boolean = isEnabled

    /**
     * 计算带有人体/环境微抖动的当前纬度（高斯分布 ±0.00005 度）。
     */
    fun getJitteredLatitude(): Double {
        val jitter = ThreadLocalRandom.current().nextGaussian() * 0.00005
        return activeLatitude + jitter
    }

    /**
     * 计算带有人体/环境微抖动的当前经度（高斯分布 ±0.00005 度）。
     */
    fun getJitteredLongitude(): Double {
        val jitter = ThreadLocalRandom.current().nextGaussian() * 0.00005
        return activeLongitude + jitter
    }

    /**
     * 拟真利雅得海拔（612.0m ± 1.5m 微漂移）。
     */
    fun getJitteredAltitude(): Double {
        val jitter = ThreadLocalRandom.current().nextGaussian() * 1.5
        return BASE_ALTITUDE + jitter
    }

    /**
     * 拟真 GPS 精度（6.8f - 12.4f 米波动）。
     */
    fun getJitteredAccuracy(): Float {
        return 7.2f + (ThreadLocalRandom.current().nextFloat() * 4.2f)
    }

    /**
     * 拟真静止/手持微动速度（0.0f - 0.25f m/s）。
     */
    fun getJitteredSpeed(): Float {
        return ThreadLocalRandom.current().nextFloat() * 0.25f
    }

    /**
     * 构建包含沙特利雅得高斯微抖动坐标与合理海拔/精度的合法 [Location] 实例。
     */
    fun createSpoofedLocation(provider: String = LocationManager.GPS_PROVIDER): Location {
        return Location(provider).apply {
            latitude = getJitteredLatitude()
            longitude = getJitteredLongitude()
            altitude = getJitteredAltitude()
            accuracy = getJitteredAccuracy()
            bearing = ThreadLocalRandom.current().nextFloat() * 360.0f
            speed = getJitteredSpeed()
            time = System.currentTimeMillis()
            elapsedRealtimeNanos = SystemClock.elapsedRealtimeNanos()
        }
    }

    private fun hookLocationMethods(module: XposedModule) {
        val locationClass = Location::class.java

        val getLatMethod = locationClass.getMethod("getLatitude")
        module.trackHook("GpsHook", getLatMethod).intercept { chain ->
            if (isFeatureEnabled()) getJitteredLatitude() else chain.proceed()
        }

        val getLngMethod = locationClass.getMethod("getLongitude")
        module.trackHook("GpsHook", getLngMethod).intercept { chain ->
            if (isFeatureEnabled()) getJitteredLongitude() else chain.proceed()
        }

        val getAltMethod = locationClass.getMethod("getAltitude")
        module.trackHook("GpsHook", getAltMethod).intercept { chain ->
            if (isFeatureEnabled()) getJitteredAltitude() else chain.proceed()
        }

        val getAccMethod = locationClass.getMethod("getAccuracy")
        module.trackHook("GpsHook", getAccMethod).intercept { chain ->
            if (isFeatureEnabled()) getJitteredAccuracy() else chain.proceed()
        }

        val getSpeedMethod = locationClass.getMethod("getSpeed")
        module.trackHook("GpsHook", getSpeedMethod).intercept { chain ->
            if (isFeatureEnabled()) getJitteredSpeed() else chain.proceed()
        }

        for (method in locationClass.declaredMethods) {
            if (method.name == "isFromMockProvider" && method.parameterCount == 0) {
                module.trackHook("GpsHook", method).intercept { chain ->
                    if (isFeatureEnabled()) false else chain.proceed()
                }
            }
        }

        Log.i(TAG, "Location 经纬度/海拔/精度微抖动与 Mock 防检测拦截器挂载完成")
    }

    private fun hookLocationManagerMethods(module: XposedModule) {
        val lmClass = LocationManager::class.java
        for (method in lmClass.declaredMethods) {
            if (Modifier.isAbstract(method.modifiers)) continue
            if (method.name == "getLastKnownLocation" && method.parameterCount == 1) {
                module.trackHook("GpsHook", method).intercept { chain ->
                    if (isFeatureEnabled()) {
                        val realResult = chain.proceed() as? Location
                        if (realResult != null) {
                            realResult.latitude = getJitteredLatitude()
                            realResult.longitude = getJitteredLongitude()
                            realResult.altitude = getJitteredAltitude()
                            realResult.accuracy = getJitteredAccuracy()
                            realResult.speed = getJitteredSpeed()
                            realResult
                        } else {
                            val provider = chain.args[0] as? String ?: LocationManager.GPS_PROVIDER
                            createSpoofedLocation(provider)
                        }
                    } else {
                        chain.proceed()
                    }
                }
            }
        }
        Log.i(TAG, "LocationManager 定位服务拦截器挂载完成")
    }

    fun init(module: XposedModule) {
        hookLocationMethods(module)
        hookLocationManagerMethods(module)
        Log.i(TAG, "系统 GPS 微抖动与海拔拟真子系统就绪")
    }
}
