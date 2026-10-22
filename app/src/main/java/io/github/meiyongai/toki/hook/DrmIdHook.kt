package io.github.meiyongai.toki.hook

import android.content.Context
import android.media.MediaDrm
import android.os.Build
import android.provider.Settings
import android.util.Log
import io.github.meiyongai.toki.provider.ConfigClient
import io.github.libxposed.api.XposedModule
import java.lang.reflect.Modifier

/**
 * 硬件标识与 DRM 唯一 ID 伪装 Hook 核心处理器（TokiDrmIdHook）。
 *
 * 拦截 Settings.Secure 的 ANDROID_ID (SSAID) 获取以及 MediaDrm 的 Widevine deviceUniqueId 属性，
 * 替换为确定性或配置驱动的硬件标识，阻断 ByteDance 跨重置（pm clear / GAID reset）硬件指纹关联。
 */
object DrmIdHook {

    private const val TAG = "TokiDrmIdHook"

    @Volatile
    private var isEnabled: Boolean = true

    /** 确定性 16 字符小写十六进制 ANDROID_ID */
    @Volatile
    private var activeAndroidId: String = "9f4a8b12c7e305d1"

    /** 确定性 32 字节 Widevine deviceUniqueId 指纹 */
    private val DETERMINISTIC_DRM_ID: ByteArray = byteArrayOf(
        0x9f.toByte(), 0x4a.toByte(), 0x8b.toByte(), 0x12.toByte(),
        0xc7.toByte(), 0xe3.toByte(), 0x05.toByte(), 0xd1.toByte(),
        0x18.toByte(), 0x27.toByte(), 0x36.toByte(), 0x45.toByte(),
        0x54.toByte(), 0x63.toByte(), 0x72.toByte(), 0x81.toByte(),
        0xa1.toByte(), 0xb2.toByte(), 0xc3.toByte(), 0xd4.toByte(),
        0xe5.toByte(), 0xf6.toByte(), 0x07.toByte(), 0x18.toByte(),
        0x29.toByte(), 0x3a.toByte(), 0x4b.toByte(), 0x5c.toByte(),
        0x5d.toByte(), 0x7e.toByte(), 0x8f.toByte(), 0x90.toByte()
    )

    fun refreshConfig(context: Context) {
        isEnabled = ConfigClient.getBoolean(context, "drm_spoof_enabled")
        val customId = ConfigClient.getString(context, "custom_android_id", defaultValue = null)
        if (!customId.isNullOrBlank() && customId.length == 16) {
            activeAndroidId = customId.lowercase()
        }
        Log.i(TAG, "DrmId 伪装状态已刷新 -> isEnabled=$isEnabled android_id=$activeAndroidId")
    }

    fun isFeatureEnabled(): Boolean = isEnabled

    /**
     * 拦截 Settings.Secure.getString 中的 android_id 查询。
     */
    private fun hookAndroidId(module: XposedModule) {
        val secureClass = Settings.Secure::class.java
        for (method in secureClass.declaredMethods) {
            if (Modifier.isAbstract(method.modifiers)) continue
            if (method.name == "getString" && method.parameterCount == 2) {
                module.trackHook("DrmIdHook", method, requiresConfiguration = false).intercept { chain ->
                    val name = chain.args[1] as? String
                    if (isFeatureEnabled() && name == Settings.Secure.ANDROID_ID) {
                        activeAndroidId
                    } else {
                        chain.proceed()
                    }
                }
            }
        }
        Log.i(TAG, "Settings.Secure.android_id 拦截器挂载完成")
    }

    /**
     * 拦截 MediaDrm.getPropertyByteArray 中的 deviceUniqueId 查询。
     */
    private fun hookMediaDrm(module: XposedModule) {
        val mediaDrmClass = MediaDrm::class.java
        for (method in mediaDrmClass.declaredMethods) {
            if (Modifier.isAbstract(method.modifiers)) continue
            if (method.name == "getPropertyByteArray" && method.parameterCount == 1 &&
                method.parameterTypes[0] == String::class.java
            ) {
                module.trackHook("DrmIdHook", method, requiresConfiguration = false).intercept { chain ->
                    val propertyName = chain.args[0] as? String
                    if (isFeatureEnabled() && (propertyName == MediaDrm.PROPERTY_DEVICE_UNIQUE_ID || propertyName == "deviceUniqueId")) {
                        DETERMINISTIC_DRM_ID
                    } else {
                        chain.proceed()
                    }
                }
            }
        }
        Log.i(TAG, "MediaDrm.getPropertyByteArray 拦截器挂载完成")
    }

    /**
     * 拦截 Build.getSerial() 保持与设备硬件指纹一致。
     */
    private fun hookBuildSerial(module: XposedModule) {
        try {
            val buildClass = Build::class.java
            for (method in buildClass.declaredMethods) {
                if (Modifier.isAbstract(method.modifiers)) continue
                if (method.name == "getSerial") {
                    module.trackHook("DrmIdHook", method, requiresConfiguration = false).intercept { chain ->
                        if (isFeatureEnabled()) "R58R12RT48N" else chain.proceed()
                    }
                }
            }
        } catch (t: Throwable) {
            Log.w(TAG, "hookBuildSerial 挂载异常: ${t.message}")
        }
    }

    fun init(module: XposedModule) {
        hookAndroidId(module)
        hookMediaDrm(module)
        hookBuildSerial(module)
        Log.i(TAG, "TokiDrmIdHook 硬件标识子系统初始化就绪")
    }
}
