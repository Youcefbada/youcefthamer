package io.github.meiyongai.toki.hook

import android.content.Context
import android.content.Intent
import android.content.pm.PackageInfo
import android.content.pm.PackageManager
import android.content.pm.ResolveInfo
import android.provider.Settings
import android.util.Log
import io.github.meiyongai.toki.provider.ConfigClient
import io.github.libxposed.api.XposedModule
import java.lang.reflect.Modifier

/**
 * 宿主与系统隐蔽保护 Hook 核心处理器（TokiStealthHook）。
 *
 * 拦截目标应用对调试模式（ADB）、开发者选项、模拟位置标记以及本地 Root/VPN 管理应用的探测，
 * 欺骗目标应用检测逻辑，规避农场设备、自动化脚本及黑名单应用检测。
 */
object StealthHook {

    private const val TAG = "TokiStealthHook"

    @Volatile
    private var isEnabled: Boolean = true

    private val BLACKLIST_PACKAGES = setOf(
        "com.v2ray.ang",
        "com.topjohnwu.magisk",
        "io.github.meiyongai.toki",
        "org.lsposed.manager",
        "bin.mt.plus",
        "com.ghisler.android.totalcommander"
    )

    private val BLACKLIST_KEYWORDS = listOf(
        "magisk", "lsposed", "xposed", "vector", "v2ray", "termux", "frida", "edxposed"
    )

    fun refreshConfig(context: Context) {
        isEnabled = ConfigClient.getBoolean(context, "stealth_spoof_enabled")
        Log.i(TAG, "Stealth 隐蔽状态已刷新 -> isEnabled=$isEnabled")
    }

    fun isFeatureEnabled(): Boolean = isEnabled

    private fun isBlacklisted(pkgName: String): Boolean {
        val lower = pkgName.lowercase()
        if (lower in BLACKLIST_PACKAGES) return true
        return BLACKLIST_KEYWORDS.any { lower.contains(it) }
    }

    /**
     * 拦截 Settings.Global 与 Settings.Secure 中关于 ADB 和开发者选项的查询。
     */
    private fun hookSettings(module: XposedModule) {
        val globalClass = Settings.Global::class.java
        for (method in globalClass.declaredMethods) {
            if (Modifier.isAbstract(method.modifiers)) continue
            when (method.name) {
                "getInt" -> {
                    module.trackHook("StealthHook", method, requiresConfiguration = false).intercept { chain ->
                        if (!isFeatureEnabled()) return@intercept chain.proceed()
                        val name = chain.args.getOrNull(1) as? String
                        when (name) {
                            "adb_enabled", "development_settings_enabled", "mock_location" -> 0
                            "animator_duration_scale", "window_animation_scale", "transition_animation_scale" -> 1
                            else -> chain.proceed()
                        }
                    }
                }
                "getString" -> {
                    module.trackHook("StealthHook", method, requiresConfiguration = false).intercept { chain ->
                        if (!isFeatureEnabled()) return@intercept chain.proceed()
                        val name = chain.args.getOrNull(1) as? String
                        when (name) {
                            "adb_enabled", "development_settings_enabled", "mock_location" -> "0"
                            "animator_duration_scale", "window_animation_scale", "transition_animation_scale" -> "1.0"
                            else -> chain.proceed()
                        }
                    }
                }
            }
        }

        val secureClass = Settings.Secure::class.java
        for (method in secureClass.declaredMethods) {
            if (Modifier.isAbstract(method.modifiers)) continue
            when (method.name) {
                "getInt" -> {
                    module.trackHook("StealthHook", method, requiresConfiguration = false).intercept { chain ->
                        if (!isFeatureEnabled()) return@intercept chain.proceed()
                        val name = chain.args.getOrNull(1) as? String
                        when (name) {
                            "adb_enabled", "development_settings_enabled", "mock_location" -> 0
                            else -> chain.proceed()
                        }
                    }
                }
                "getString" -> {
                    module.trackHook("StealthHook", method, requiresConfiguration = false).intercept { chain ->
                        if (!isFeatureEnabled()) return@intercept chain.proceed()
                        val name = chain.args.getOrNull(1) as? String
                        when (name) {
                            "adb_enabled", "development_settings_enabled", "mock_location" -> "0"
                            else -> chain.proceed()
                        }
                    }
                }
            }
        }
        Log.i(TAG, "Settings.Global 与 Settings.Secure 拦截器挂载完成")
    }

    /**
     * 拦截 SystemProperties 查询，隐蔽 USB 调试、adbd 服务及 root 标记。
     */
    private fun hookSystemProperties(module: XposedModule) {
        try {
            val sysPropClass = Class.forName("android.os.SystemProperties")
            for (method in sysPropClass.declaredMethods) {
                if (Modifier.isAbstract(method.modifiers)) continue
                if (method.name == "get") {
                    if (method.parameterCount == 1 && method.parameterTypes[0] == String::class.java) {
                        module.trackHook("StealthHook", method, requiresConfiguration = false).intercept { chain ->
                            if (!isFeatureEnabled()) return@intercept chain.proceed()
                            val key = chain.args[0] as? String
                            when (key) {
                                "sys.usb.state", "sys.usb.config" -> "mtp"
                                "init.svc.adbd" -> "stopped"
                                "ro.debuggable" -> "0"
                                "ro.secure" -> "1"
                                "ro.build.tags" -> "release-keys"
                                "ro.build.type" -> "user"
                                else -> chain.proceed()
                            }
                        }
                    } else if (method.parameterCount == 2 &&
                        method.parameterTypes[0] == String::class.java &&
                        method.parameterTypes[1] == String::class.java
                    ) {
                        module.trackHook("StealthHook", method, requiresConfiguration = false).intercept { chain ->
                            if (!isFeatureEnabled()) return@intercept chain.proceed()
                            val key = chain.args[0] as? String
                            val def = chain.args[1] as? String
                            when (key) {
                                "sys.usb.state", "sys.usb.config" -> "mtp"
                                "init.svc.adbd" -> "stopped"
                                "ro.debuggable" -> "0"
                                "ro.secure" -> "1"
                                "ro.build.tags" -> "release-keys"
                                "ro.build.type" -> "user"
                                else -> chain.proceed()
                            }
                        }
                    }
                }
            }
            Log.i(TAG, "SystemProperties 隐蔽拦截器挂载完成")
        } catch (t: Throwable) {
            Log.w(TAG, "hookSystemProperties 挂载异常: ${t.message}")
        }
    }

    /**
     * 拦截 PackageManager 包管理查询，隐藏 v2rayNG、Magisk、LSPosed 等工具。
     */
    private fun hookPackageManager(module: XposedModule) {
        try {
            val pmClass = Class.forName("android.app.ApplicationPackageManager")
            for (method in pmClass.declaredMethods) {
                if (Modifier.isAbstract(method.modifiers)) continue
                when (method.name) {
                    "getInstalledPackages" -> {
                        module.trackHook("StealthHook", method, requiresConfiguration = false).intercept { chain ->
                            val result = chain.proceed() as? List<*> ?: return@intercept chain.proceed()
                            if (!isFeatureEnabled()) return@intercept result
                            result.filterNot { item ->
                                val pkgName = (item as? PackageInfo)?.packageName ?: ""
                                isBlacklisted(pkgName)
                            }
                        }
                    }
                    "getInstalledApplications" -> {
                        module.trackHook("StealthHook", method, requiresConfiguration = false).intercept { chain ->
                            val result = chain.proceed() as? List<*> ?: return@intercept chain.proceed()
                            if (!isFeatureEnabled()) return@intercept result
                            result.filterNot { item ->
                                val appInfo = item as? android.content.pm.ApplicationInfo
                                val pkgName = appInfo?.packageName ?: ""
                                isBlacklisted(pkgName)
                            }
                        }
                    }
                    "getPackageInfo" -> {
                        if (method.parameterCount >= 1 && method.parameterTypes[0] == String::class.java) {
                            module.trackHook("StealthHook", method, requiresConfiguration = false).intercept { chain ->
                                val pkgName = chain.args[0] as? String
                                if (isFeatureEnabled() && pkgName != null && isBlacklisted(pkgName)) {
                                    throw PackageManager.NameNotFoundException("Package not found: $pkgName")
                                }
                                chain.proceed()
                            }
                        }
                    }
                    "getApplicationInfo" -> {
                        if (method.parameterCount >= 1 && method.parameterTypes[0] == String::class.java) {
                            module.trackHook("StealthHook", method, requiresConfiguration = false).intercept { chain ->
                                val pkgName = chain.args[0] as? String
                                if (isFeatureEnabled() && pkgName != null && isBlacklisted(pkgName)) {
                                    throw PackageManager.NameNotFoundException("Application not found: $pkgName")
                                }
                                chain.proceed()
                            }
                        }
                    }
                    "queryIntentActivities" -> {
                        module.trackHook("StealthHook", method, requiresConfiguration = false).intercept { chain ->
                            val result = chain.proceed() as? List<*> ?: return@intercept chain.proceed()
                            if (!isFeatureEnabled()) return@intercept result
                            result.filterNot { item ->
                                val resInfo = item as? ResolveInfo
                                val actPkg = resInfo?.activityInfo?.packageName ?: ""
                                isBlacklisted(actPkg)
                            }
                        }
                    }
                }
            }
            Log.i(TAG, "ApplicationPackageManager 敏感包过滤拦截器挂载完成")
        } catch (t: Throwable) {
            Log.w(TAG, "hookPackageManager 挂载异常: ${t.message}")
        }
    }

    fun init(module: XposedModule) {
        hookSettings(module)
        hookSystemProperties(module)
        hookPackageManager(module)
        Log.i(TAG, "TokiStealthHook 隐蔽子系统初始化就绪")
    }
}
