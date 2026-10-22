package io.github.meiyongai.toki.hook

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.util.Log
import io.github.meiyongai.toki.provider.ConfigClient
import io.github.libxposed.api.XposedModule
import java.lang.reflect.Modifier
import java.net.NetworkInterface
import java.util.Collections
import java.util.Enumeration

/**
 * 网络通道与 VPN 隐蔽保护 Hook 核心处理器（TokiNetworkHook）。
 *
 * 拦截 NetworkCapabilities、NetworkInterface、ConnectivityManager 以及系统代理属性，
 * 隐藏 tun0、ppp0 虚拟接口，伪装为正常原生 Wi-Fi 连接，规避 TikTok 风控引擎对 VPN 的识别。
 */
object NetworkHook {

    private const val TAG = "TokiNetworkHook"

    @Volatile
    private var isEnabled: Boolean = true

    private val PROXY_PROPERTIES = setOf(
        "http.proxyHost", "http.proxyPort",
        "https.proxyHost", "https.proxyPort",
        "socksProxyHost", "socksProxyPort"
    )

    fun refreshConfig(context: Context) {
        isEnabled = ConfigClient.getBoolean(context, "network_spoof_enabled")
        Log.i(TAG, "Network 伪装状态已刷新 -> isEnabled=$isEnabled")
    }

    fun isFeatureEnabled(): Boolean = isEnabled

    private fun isVpnInterface(name: String): Boolean {
        val lower = name.lowercase()
        return lower == "tun0" || lower == "ppp0" || lower.startsWith("tun") || lower.startsWith("tap")
    }

    /**
     * 拦截 NetworkCapabilities，抹除 TRANSPORT_VPN 标记并注入 TRANSPORT_WIFI。
     */
    private fun hookNetworkCapabilities(module: XposedModule) {
        val netCapClass = NetworkCapabilities::class.java
        for (method in netCapClass.declaredMethods) {
            if (Modifier.isAbstract(method.modifiers)) continue
            when (method.name) {
                "hasTransport" -> {
                    module.trackHook("NetworkHook", method, requiresConfiguration = false).intercept { chain ->
                        if (!isFeatureEnabled()) return@intercept chain.proceed()
                        val type = chain.args[0] as? Int
                        when (type) {
                            NetworkCapabilities.TRANSPORT_VPN -> false
                            NetworkCapabilities.TRANSPORT_WIFI -> true
                            else -> chain.proceed()
                        }
                    }
                }
                "hasCapability" -> {
                    module.trackHook("NetworkHook", method, requiresConfiguration = false).intercept { chain ->
                        if (!isFeatureEnabled()) return@intercept chain.proceed()
                        val cap = chain.args[0] as? Int
                        when (cap) {
                            NetworkCapabilities.NET_CAPABILITY_NOT_VPN -> true
                            else -> chain.proceed()
                        }
                    }
                }
            }
        }
        Log.i(TAG, "NetworkCapabilities 拦截器挂载完成")
    }

    /**
     * 拦截 NetworkInterface，过滤或重命名 tun0/ppp0。
     */
    private fun hookNetworkInterfaces(module: XposedModule) {
        val netIfClass = NetworkInterface::class.java
        for (method in netIfClass.declaredMethods) {
            if (Modifier.isAbstract(method.modifiers)) continue
            when (method.name) {
                "getName", "getDisplayName" -> {
                    module.trackHook("NetworkHook", method, requiresConfiguration = false).intercept { chain ->
                        val originalName = chain.proceed() as? String ?: return@intercept chain.proceed()
                        if (!isFeatureEnabled()) return@intercept originalName
                        if (isVpnInterface(originalName)) "wlan0" else originalName
                    }
                }
                "getNetworkInterfaces" -> {
                    module.trackHook("NetworkHook", method, requiresConfiguration = false).intercept { chain ->
                        val result = chain.proceed() as? Enumeration<NetworkInterface> ?: return@intercept chain.proceed()
                        if (!isFeatureEnabled()) return@intercept result
                        val filteredList = result.toList().filterNot { iface ->
                            isVpnInterface(iface.name)
                        }
                        Collections.enumeration(filteredList)
                    }
                }
            }
        }
        Log.i(TAG, "NetworkInterface 拦截器挂载完成")
    }

    /**
     * 拦截 ConnectivityManager，阻止获取 VPN 网络连接信息。
     */
    private fun hookConnectivityManager(module: XposedModule) {
        val connClass = ConnectivityManager::class.java
        for (method in connClass.declaredMethods) {
            if (Modifier.isAbstract(method.modifiers)) continue
            if (method.name == "getNetworkInfo" && method.parameterCount == 1 &&
                method.parameterTypes[0] == Int::class.javaPrimitiveType
            ) {
                module.trackHook("NetworkHook", method, requiresConfiguration = false).intercept { chain ->
                    if (!isFeatureEnabled()) return@intercept chain.proceed()
                    val type = chain.args[0] as? Int
                    if (type == ConnectivityManager.TYPE_VPN) {
                        null
                    } else {
                        chain.proceed()
                    }
                }
            }
        }
        Log.i(TAG, "ConnectivityManager 拦截器挂载完成")
    }

    /**
     * 拦截 System.getProperty 代理参数。
     */
    private fun hookProxyProperties(module: XposedModule) {
        val sysClass = System::class.java
        for (method in sysClass.declaredMethods) {
            if (Modifier.isAbstract(method.modifiers)) continue
            if (method.name == "getProperty") {
                if (method.parameterCount == 1 && method.parameterTypes[0] == String::class.java) {
                    module.trackHook("NetworkHook", method, requiresConfiguration = false).intercept { chain ->
                        if (!isFeatureEnabled()) return@intercept chain.proceed()
                        val prop = chain.args[0] as? String
                        if (prop in PROXY_PROPERTIES) null else chain.proceed()
                    }
                } else if (method.parameterCount == 2 &&
                    method.parameterTypes[0] == String::class.java &&
                    method.parameterTypes[1] == String::class.java
                ) {
                    module.trackHook("NetworkHook", method, requiresConfiguration = false).intercept { chain ->
                        if (!isFeatureEnabled()) return@intercept chain.proceed()
                        val prop = chain.args[0] as? String
                        val def = chain.args[1] as? String
                        if (prop in PROXY_PROPERTIES) def else chain.proceed()
                    }
                }
            }
        }
        Log.i(TAG, "System.getProperty 代理过滤拦截器挂载完成")
    }

    fun init(module: XposedModule) {
        hookNetworkCapabilities(module)
        hookNetworkInterfaces(module)
        hookConnectivityManager(module)
        hookProxyProperties(module)
        Log.i(TAG, "TokiNetworkHook 网络隐蔽子系统初始化就绪")
    }
}
