# 🇸🇦 توثيق وتفعيل منظومة الـ VPN التلقائي للهاتف (KSA TikTok Enterprise)
# Automated Saudi VPN Autostart & Watchdog Architecture Manual

**معرف الوثيقة:** `TOKI-VPN-AUTO-AR-002`  
**تاريخ التنفيذ:** 23 أكتوبر 2026  
**الجهاز المستهدف:** Samsung Galaxy A02 (`SM-A022F` / `a02xx`)  
**نظام التشغيل:** أندرويد 11 (One UI Core 3.1 / API 30 / Magisk v30.7 Root)  
**الحالة:** ⚠️ تم إيقاف وحذف المنظومة التلقائية وإلغاء تثبيت الشيطان من الهاتف بناءً على طلب المستخدم (التحكم يدوي بالكامل)  

> [!NOTE]
> تم إزالة خدمة الإقلاع التلقائي والمراقبة (`94-vpn-autostart-daemon.sh`) من Magisk وإلغاء ضبط `always_on_vpn_app`، واستعادة التحكم اليدوي الطبيعي بتطبيق الـ VPN دون أي فتح أو نقر تلقائي.

---

## 1. ملخص ما تم إنجازه (Executive Summary)

بناءً على طلبك بجعل الـ VPN يعمل تلقائياً وبشكل ذاتي بمجرد **فتح الهاتف أو إعادة تشغيله أو استيقاظه من وضع السكون**، تم تصميم ونشر منظومة متكاملة من الخدمات الدائمة وأدوات المراقبة الذاتية على الهاتف، بحيث:
1. **لا تحتاج نهائياً للنقر على أي زر أو فتح تطبيق الـ VPN يدوياً.**
2. عند إقلاع الهاتف (Reboot / Power On)، تقوم خدمة Magisk التلقائية بانتظار اتصال الواي فاي ثم فتح الاتصال السعودي فوراً وإخفاء التطبيق في الخلفية والعودة للشاشة الرئيسية.
3. عند قفل الهاتف وإعادة فتحه (Unlock / Screen Wake)، يتأكد الحارس الذاتي من بقاء نفق الـ VPN (`tun0`) نشطاً ومتصلاً بالعاصمة الرياض.
4. في حال حدوث أي انقطاع مفاجئ بالشبكة أو إغلاق التطبيق بواسطة نظام أندرويد بسبب ضيق الذاكرة، يقوم شيطان المراقبة فورياً (خلال ثوانٍ) بإعادة الاتصال تلقائياً بدون أي تدخل منك.

---

## 2. تفاصيل الجهاز وفحصه (Connected Device Audit)

| العنصر | المواصفات الفعلية للجهاز |
| :--- | :--- |
| **موديل الهاتف** | `Samsung Galaxy A02` (`SM-A022F`) |
| **إصدار أندرويد** | أندرويد 11 (API Level 30) |
| **صلاحيات الروت** | Magisk `v30.7` بصلاحيات كاملة `uid=0(root)` |
| **مزود الـ VPN المعتمد** | `Urban VPN` (`com.urbanvpn.android`) بمحرك `OpenVPN` العتادي (`libpie_openvpn.armeabi-v7a.so`) |
| **خادم الاتصال المستهدف** | الرياض - المملكة العربية السعودية (`SA.Asia.Saudi Arabia R3.ovpn`) |
| **عنوان الـ IP الخارجي المحقق** | `146.70.167.70` (الرياض، المملكة العربية السعودية 🇸🇦) |

---

## 3. المكونات والخدمات البرمجية التي تم إنشاؤها ونشرها

### 1. شيطان المراقبة والإقلاع التلقائي الدائم (`94-vpn-autostart-daemon.sh`)
* **المسار على الهاتف:** `/data/adb/service.d/94-vpn-autostart-daemon.sh` (صلاحيات `chmod 755`)
* **المسار في المستودع:** [`research/tools/94-vpn-autostart-daemon.sh`](file:///c:/Users/Youcef/Desktop/Toki/research/tools/94-vpn-autostart-daemon.sh)
* **الوظيفة:**
  - يعمل تلقائياً كخدمة Magisk أثناء بدء تشغيل الهاتف (`sys.boot_completed=1`).
  - يضبط إعداد أندرويد الدائم: `settings put secure always_on_vpn_app com.urbanvpn.android`.
  - يراقب حالة نفق الـ VPN (`tun0`) كل 5 ثوانٍ.
  - إذا وجد النفق مغلقاً، يقوم فوراً بإيقاظ الشاشة، تشغيل Urban VPN، الضغط التلقائي على خادم السعودية، التحقق من ظهور نفق `tun0`، ثم إرسال أمر `HOME` ليعود الهاتف نظيفاً للشاشة الرئيسية دون إزعاج المستخدم.
  - يحصن عمليات الـ VPN بمعامل الذاكرة `-900` لمنع النظام من قتلها.

### 2. ترقية حارس الذاكرة OOM Guard (`98-vpn-oom-guard.sh`)
* **المسار على الهاتف:** `/data/adb/service.d/98-vpn-oom-guard.sh`
* **المسار في المستودع:** [`research/tools/98-vpn-oom-guard.sh`](file:///c:/Users/Youcef/Desktop/Toki/research/tools/98-vpn-oom-guard.sh)
* **التعديل المضاف:**
  - تم توسيع نطاق الحماية لـ Galaxy A02 ليشمل: `com.urbanvpn.android` ومحرك النواة `libpie_openvpn` بجانب `com.v2ray.ang`.
  - يمنح عمليات الـ VPN حصانة مطلقة (`oom_score_adj -900`) ضد Low Memory Killer (LMK) عند معالجة الفيديوهات الثقيلة أو قفل الشاشة لفترة طويلة.

### 3. أداة إدارة الـ VPN المتطورة للكمبيوتر (`vpn_manager.py`)
* **المسار في المستودع:** [`automation/vpn_manager.py`](file:///c:/Users/Youcef/Desktop/Toki/automation/vpn_manager.py)
* **طريقة الاستخدام من موجه الأوامر (Terminal / CMD):**
  - **عرض الحالة والـ IP والمدينة:**
    ```bash
    python automation/vpn_manager.py status
    ```
  - **فحص سجلات الحارس التلقائي (Logs):**
    ```bash
    python automation/vpn_manager.py logs
    ```
  - **الاتصال التلقائي الفوري:**
    ```bash
    python automation/vpn_manager.py connect
    ```
  - **قطع الاتصال:**
    ```bash
    python automation/vpn_manager.py disconnect
    ```
  - **إعادة تثبيت أو ترقية الخدمة على الهاتف:**
    ```bash
    python automation/vpn_manager.py install-daemon
    ```

---

## 4. نتائج الاختبارات العملية والميدانية (Empirical Verification)

### الاختبار الأول: قطع الاتصال القسري ومراقبة الاستعادة الذاتية
1. تم إرسال أمر إيقاف إجباري للتطبيق (`am force-stop com.urbanvpn.android`).
2. تم رصد إشعار الحارس الفوري في السجلات:
   ```log
   [ALERT] tun0 is DOWN. Reconnecting...
   [RECONNECT] Triggering Urban VPN automatic connection...
   [SUCCESS] tun0 is UP!
   ```
3. تمت استعادة النفق التشفيري ونجح الاتصال بنسبة 100% وعاد الهاتف للشاشة الرئيسية تلقائياً.

### الاختبار الثاني: فحص دورة سكون واستيقاظ الشاشة (Sleep / Wake Cycle)
1. تم إطفاء الشاشة وإدخال الجهاز في وضع السكون الكامل (`input keyevent 26`).
2. تمت إعادة تشغيل الشاشة (`input keyevent 224`).
3. تم التحقق من نفق `tun0` ووجد نشطاً ومستقراً بالكامل بدون أي تسريب للبيانات.

### الاختبار الثالث: الفحص السريري الشامل لسلامة النظام (Pre-Flight Health Gate)
تم تشغيل الفحص الكامل عبر [`automation/preflight_check.py`](file:///c:/Users/Youcef/Desktop/Toki/automation/preflight_check.py):
```text
======================================================================
   KSA TIKTOK PHASE-3 ENTERPRISE PRE-FLIGHT HEALTH GATE
   Device: Samsung Galaxy A02 (SM-A022F) | OS: Android 11 API 30
======================================================================
[01/28] [PASS]  VPN Application Active Status: Active VPN Process Count=7
[02/28] [PASS]  Always-on VPN Routing Target: app=com.urbanvpn.android
[03/28] [PASS]  VPN Process Running: PIDs=['2844', '22627', '23887', '24190']
[04/28] [PASS]  VPN tun0 Network Interface: tun0 status: UP
[05/28] [PASS]  Saudi Arabia Exit IP Routing: IP=146.70.167.70 (City=Riyadh, Country=SA)
[06/28] [PASS]  ip6tables OUTPUT Drop Policy: OUTPUT policy DROP verified
...
[28/28] [PASS]  ZRAM Swappiness = 100: vm.swappiness=100
======================================================================
PRE-FLIGHT GATE RESULT: 28/28 CHECKS PASSED
[STATUS: ZERO LEAK PASS] Device is fully hardened and ready for TikTok session!
```

---

## 5. دليل الاستخدام اليومي للمستخدم (User Daily Guide)

* **ماذا عليك أن تفعل الآن؟**
  * لا شيء على الإطلاق! الـ VPN يعمل تلقائياً وبشكل صامت في خلفية هاتفك.
  * كلما فتحت الهاتف، ستلاحظ وجود رمز المفتاح 🔑 في أعلى الشاشة مشيراً إلى اتصالك الآمن عبر خادم الرياض.
  * يمكنك مباشرة فتح تطبيق تيك توك، أو تشغيل أدوات الأتمتة:
    ```bash
    python automation/ksa_human_agent.py 20
    ```
  * وإذا أردت في أي وقت التأكد من الـ IP من الكمبيوتر، نفذ:
    ```bash
    python automation/vpn_manager.py status
    ```
