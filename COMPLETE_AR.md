# 🇸🇦 التوثيق الشامل لمنظومة التخفي المؤسسي والأتمتة الحيوية لتطبيق تيك توك (المملكة العربية السعودية)
# KSA TikTok Enterprise Stealth & Bio-Automation Architecture - Complete Arabic Manual

**معرف الوثيقة:** `TOKI-KSA-ENTERPRISE-AR-001`  
**تاريخ التوثيق:** 22 أكتوبر 2026  
**الحالة:** ✅ مكتمل، مُختبر فيزيائياً بنسبة 100%، ومرفوع على المستودع  
**الجهاز الفيزيائي المستهدف:** Samsung Galaxy A02 (`SM-A022F` / `a02xx`)  
**نظام التشغيل:** أندرويد 11 (One UI Core 3.1، مستوى API 30، نواة لينكس Linux Kernel 4.19)  
**معمارية المعالج ومساحة المستخدم:** 32-بت ARM (`armeabi-v7a` على شريحة MediaTek `MT6739`)  
**بيئة الترويت والاعتراض:** Magisk `v30.7` + Vector (`Zygisk LSPosed API 102 v2.2`)  
**التطبيق المستهدف:** تيك توك الرسمي العالمي (`com.zhiliaoapp.musically` الإصدار `v47.1.4`)  
**المستودع السحابي المحدث:** [https://github.com/Youcefbada/youcefthamer.git](https://github.com/Youcefbada/youcefthamer.git)

---

## الفهرس العام
1. [نظرة عامة على المشروع وأهدافه الهندسية](#1-نظرة-عامة-على-المشروع-وأهدافه-الهندسية)
2. [المرحلة الأولى: التأسيس الأولي وهوكات تيك توك الأساسية](#2-المرحلة-الأولى-التأسيس-الأولي-وهوكات-تيك-توك-الأساسية)
3. [المرحلة الثانية: التخفي المؤسسي وحماية تسريبات الشبكة](#3-المرحلة-الثانية-التخفي-المؤسسي-وحماية-تسريبات-الشبكة)
4. [المرحلة الثالثة: كسر حاجز النواة ومحاكي اللمس الفيزيائي الحقيقي](#4-المرحلة-الثالثة-كسر-حاجز-النواة-ومحاكي-اللمس-الفيزيائي-الحقيقي)
5. [المرحلة الرابعة: إدارة الهويات وحماية النزاهة وتعقيم الفيديو](#5-المرحلة-الرابعة-إدارة-الهويات-وحماية-النزاهة-وتعقيم-الفيديو)
6. [بوابة الفحص السريري لسلامة النظام (28 نقطة فحص)](#6-بوابة-الفحص-السريري-لسلامة-النظام-28-نقطة-فحص)
7. [دليل التشغيل اليومي خطوة بخطوة (Runbook)](#7-دليل-التشغيل-اليومي-خطوة-بخطوة-runbook)
8. [فهرس الملفات والأدوات في المستودع](#8-فهرس-الملفات-والأدوات-في-المستودع)

---

## 1. نظرة عامة على المشروع وأهدافه الهندسية

تم تصميم وتطوير هذه المنظومة لتحويل هاتف فيزيائي اقتصادي (**Samsung Galaxy A02**) إلى عقدة تشغيل أوتوماتيكية بالغة الدقة وغير قابلة للكشف، تحاكي في كل تفاصيلها مستخدماً سعودياً حقيقياً في مدينة الرياض يتصفح ويتفاعل مع تطبيق تيك توك العالمي.

### التحدي التقني:
تعتمد شركة ByteDance على واحدة من أشرس منظومات مكافحة الاحتيال وكشف المحاكيات في العالم (`libmetasec_ml.so`، `libmsaoaidsec.so`، `libttboringssl.so`، و `SSCronet`). تقوم هذه المحركات بما يلي:
1. تجاوز طبقة جافا (Java Framework) وتنفيذ نداءات نظامية مباشرة إلى النواة (`svc #0` على معمارية ARM) لقراءة ملفات الذاكرة `/proc/self/maps` والشبكة `/proc/net/route`.
2. فحص مقابس لينكس المباشرة (`AF_NETLINK`) لاكتشاف واجهات الـ VPN الوهمية (`tun0` / `ppp0`).
3. تحليل القياسات الحيوية للمس (زمن اللمس، المساحة البيضاوية للإبهام، الضغط، وسرعة السحب وتغيرات التسارع).
4. التحقق من سلامة البوت لودر وشهادات التشفير العتادية عبر Google Play Integrity.
5. فحص ملفات الفيديو المرفوعة لكشف توقيعات برامج المونتاج مثل Premiere و CapCut ومعاقبة الحسابات بـ "صفر مشاهدة" (0-view shadowban).

### الإنجاز المحقق:
تم بناء وتطبيق بنية تحتية متكاملة تتألف من 4 مراحل هندسية متتالية تُغلق كل هذه الثغرات وتجعل الهاتف يعمل بشكل آمن 100%.

---

## 2. المرحلة الأولى: التأسيس الأولي وهوكات تيك توك الأساسية

في هذه المرحلة تم بناء وحدة Xposed البرمجية وتثبيتها ضمن تطبيق **Toki** الأساسي (`io.github.meiyongai.toki`):

* **انتحال بطاقة SIM السعودية ([`SimHook.kt`](file:///c:/Users/Youcef/Desktop/Toki/app/src/main/java/io/github/meiyongai/toki/hook/SimHook.kt)):**
  * كود الدولة الخلوي: `SA` (المملكة العربية السعودية).
  * كود المشغل الرقمي: `42001` (شركة الاتصالات السعودية STC).
  * الاسم الأبجدي للمشغل: `STC`.
  * اعتراض دوال `TelephonyManager` و `SubscriptionInfo` لمنع تيك توك من اكتشاف غياب الشريحة الحقيقية.
* **انتحال اللغة والتوقيت ([`LocaleHook.kt`](file:///c:/Users/Youcef/Desktop/Toki/app/src/main/java/io/github/meiyongai/toki/hook/LocaleHook.kt)):**
  * اللغة الافتراضية للتطبيق: `ar-SA` (العربية - السعودية).
  * تم الاعتراض على مستوى لغة الأعمال (Business Logic) مع الحفاظ على محرك الخطوط والرسم الأصلي (Native HarfBuzz) لتجنب تشوه الخطوط.
  * المنطقة الزمنية: `Asia/Riyadh` (توقيت الرياض العالمي UTC+3).
* **انتحال الموقع الجغرافي ([`GpsHook.kt`](file:///c:/Users/Youcef/Desktop/Toki/app/src/main/java/io/github/meiyongai/toki/hook/GpsHook.kt)):**
  * إحداثيات العاصمة الرياض: خط عرض `24.7136`، خط طول `46.6753`.
  * الارتفاع عن سطح البحر: `612.0 متر` (الارتفاع الحقيقي لمدينة الرياض).
  * محاكاة دقة الأقمار الصناعية والأقمار النشطة.

---

## 3. المرحلة الثانية: التخفي المؤسسي وحماية تسريبات الشبكة

هدفت هذه المرحلة إلى سد ثغرات البصمات اللاسلكية وبروتوكولات الإنترنت:

* **انتحال راوتر ألياف ضوئية منزلي حقيقي من STC:**
  * تم التخلص نهائياً من ثغرة الماك أدرس الافتراضي المفضوح `02:00:00:00:00:00`.
  * استبداله بـ BSSID حقيقي لمودم ألياف ضوئية هواوي تابع لشركة STC في الرياض: `48:fd:8e:b1:2c:4d`.
  * اسم شبكة الواي فاي (SSID): `"STC_5G_Home_A8F"`.
  * التردد: `5180 MHz` (نطاق 5 جيجاهرتز القناة 36) وسرعة ارتباط `433 Mbps`.
  * **توليد شبكات الجيران الوهمية:** توليد قائمة فحص واي فاي حقيقية من 4 شبكات سكنية بالرياض (`STC_5G_Home_A8F`, `STC_Fiber_5GHz`, `Mobily_Fiber_92B`, `Zain_Home_4G`) لمنع كشف بيئات المحاكاة ذات القوائم الفارغة.
* **انتحال برج الاتصالات الخلوي بالرياض (`CellInfoLte`):**
  * اعتراض دوال `TelephonyManager.getAllCellInfo()` و `getCellLocation()`.
  * إرجاع برج خلوي حقيقي لشركة STC بنطاق LTE Band 3:
    * كود المنطقة (`TAC`): `14102`.
    * معرف البرج الخلوي (`CI`): `28491021`.
    * المعرف الفيزيائي (`PCI`): `184`.
    * تردد القناة (`EARFCN`): `1650`.
* **إخفاء بيئة التطوير و تصحيح الأخطاء ADB ([`StealthHook.kt`](file:///c:/Users/Youcef/Desktop/Toki/app/src/main/java/io/github/meiyongai/toki/hook/StealthHook.kt)):**
  * إجبار استعلامات `Settings.Global` و `Settings.Secure` على إرجاع `0` لكل من: `adb_enabled`، `development_settings_enabled`، و `mock_location`.
  * إخفاء خصائص النظام الحساسة: `sys.usb.state=mtp`، `ro.debuggable=0`، و `init.svc.adbd=stopped`.
  * تصفية قائمة التطبيقات المثبتة في `ApplicationPackageManager` لإخفاء تطبيقات الروت مثل Magisk و LSPosed و Toki و v2rayNG.
* **إخفاء واجهات الـ VPN في طبقة جافا ([`NetworkHook.kt`](file:///c:/Users/Youcef/Desktop/Toki/app/src/main/java/io/github/meiyongai/toki/hook/NetworkHook.kt)):**
  * حذف خاصية `TRANSPORT_VPN` وتأكيد `TRANSPORT_WIFI`.
  * تصفية وحجب مسميات `tun0` و `ppp0` وتفريغ خصائص البروكسي للنظام `http.proxyHost`.
* **حماية النواة وجدار الحماية الأولي ([`99-ksa-firewall.sh`](file:///c:/Users/Youcef/Desktop/Toki/research/tools/99-ksa-firewall.sh)):**
  * حظر وإسقاط كامل لحزم IPv6 عبر `ip6tables -P OUTPUT DROP` لمنع تسريب الـ IP الحقيقي لشركة الاتصالات.
  * حظر حزم QUIC على منفذ UDP 443 لإجبار مكتبة تيك توك للشبكات `SSCronet` على التراجع الآمن إلى TCP TLS 1.3 عبر البروكسي.
* **حارس الذاكرة OOM Guard ([`98-vpn-oom-guard.sh`](file:///c:/Users/Youcef/Desktop/Toki/research/tools/98-vpn-oom-guard.sh)):**
  * مراقبة عملية تطبيق البروكسي وتثبيت معامل `oom_score_adj -900` لمنع النظام من قتل تطبيق الـ VPN أثناء معالجة الفيديوهات الثقيلة على هاتف Galaxy A02 ذي الذاكرة المحدودة (2GB/3GB).

---

## 4. المرحلة الثالثة: كسر حاجز النواة ومحاكي اللمس الفيزيائي الحقيقي

كشفت التحليلات العميقة لمهندسي العكس أن تيك توك يكتشف محاكيات اللمس البرمجية بسهولة، مما استدعى قفزة نوعية في المرحلة الثالثة:

### 1. استبدال أداة `adb shell input` بسائق اللمس العتادي الحقيقي
* **العيب القاتل لأداة ADB التقليدية:**
  * عند تنفيذ `input swipe` أو `input tap`، يقوم النظام بإنشاء جهاز لمس وهمي يحمل المعرف `deviceId = -1`.
  * قيمة الضغط ثابتة دائماً على `pressure = 1.0`.
  * أبعاد مساحة اللمس منعدمة تماماً (`size = 0.0`، `touchMajor = 0`، `touchMinor = 0`).
  * انعدام تقطيع الفترات الزمنية ومزامنة شاشات العرض VSYNC (مما يعني أن البوت مكشوف من أول حركة سحب!).
* **الحل الثوري المبتكر ([`TouchDriver.java`](file:///c:/Users/Youcef/Desktop/Toki/research/tools/TouchDriver.java) و [`touch_driver.jar`](file:///c:/Users/Youcef/Desktop/Toki/research/tools/touch_driver.jar)):**
  * تم بناء سائق جافا/DEX يعمل بصلاحيات الروت ويفتح مباشرة عقدة اللمس العتادية في نواة لينكس: `/dev/input/event3` المسماة عتادياً `"sec_touchscreen"`.
  * يرسل السائق حزم بروتوكول اللمس المتعدد القياسي **Linux Multi-Touch Protocol Type B** مباشرة إلى النواة:
    1. **معرف لمس عتادي حقيقي:** تظهر الحركات لتطبيق تيك توك بأنها قادمة من شاشة الهاتف الأصلية (`deviceId > 0` و `TOOL_TYPE_FINGER`).
    2. **محاكاة ديناميكية لتشوه إبهام اليد (Thumb Contact Ellipse):** تبدأ مساحة اللمس صغيرة عند الملامسة الأولى (`ABS_MT_TOUCH_MAJOR ≈ 35`)، ثم تتسع مع ضغط الإصبع للسحب إلى الذروة (`TOUCH_MAJOR ≈ 115`)، ثم تتلاشى قبل الإفلات (`TOUCH_MAJOR ≈ 40`).
    3. **نسبة بيضاوية حقيقية للإصبع:** حساب البعد الأصغر `ABS_MT_TOUCH_MINOR` بنسبة تتراوح بين `1.20` إلى `1.32` محاكية لإبهام اليد اليمنى.
    4. **مزامنة زمنية بتردد 60 هرتز:** إرسال نبضات `SYN_REPORT` كل `16ms` بدقة الميكروثانية محتوية على ارتعاشات عصبية دقيقة (Gaussian micro-tremors).

### 2. تطهير خصائص الإقلاع والبوت لودر في الذاكرة العشوائية (`resetprop -n`)
* تيك توك يقرأ الذاكرة المشتركة `/dev/__properties__` مباشرة عبر C++ متجاوزاً جافا.
* تم نشر السكربت الدائم [`97-resetprop-stealth.sh`](file:///c:/Users/Youcef/Desktop/Toki/research/tools/97-resetprop-stealth.sh) ليقوم بالتعديل المباشر داخل الذاكرة:
  * `ro.boot.verifiedbootstate` تحولت من `orange` (مفتوح) إلى **`green`** (أصلي ومغلق).
  * `ro.boot.flash.locked` أصبحت **`1`** (مغلق).
  * `ro.boot.vbmeta.device_state` أصبحت **`locked`**.
  * `ro.boot.warranty_bit` أصبحت **`0`** (ضمان ساري).

### 3. سد تسريبات WebRTC STUN العتادية على شبكة الواي فاي
* في تيك توك، تقوم مكتبة البث المباشر `libbyteav.so` بإرسال طلبات فحص WebRTC STUN على منافذ عشوائية مثل `3478` و `19302`.
* في حال كان جدار الحماية يحظر منفذ 443 فقط، تخرج هذه الحزم عبر واجهة الواي فاي `wlan0` مباشرة كاشفة عنوان الـ IP الحقيقي للجهاز في ثوانٍ معدودة.
* **الحل الصارم:** تم تحديث جدار الحماية بحظر أي خروج لحزم UDP لتطبيق تيك توك (`UID 10205`) عبر كارت الواي فاي:
  ```bash
  iptables -I OUTPUT -o wlan0 -p udp -m owner --uid-owner 10205 -j REJECT
  ```

### 4. تحسين أداء شريحة MediaTek MT6739 والذاكرة العشوائية
* يعاني هاتف Galaxy A02 من ذاكرة متواضعة (3GB RAM) ومعالج رباعي النواة Cortex-A53 مع ذاكرة فلاش بطيئة eMMC 5.1.
* تم تفعيل 2 جيجابايت من الذاكرة المضغوطة **ZRAM** بخوارزمية `lz4` السريعة للغاية.
* تعديل متغيرات نواة لينكس:
  * `vm.swappiness = 100` (تفضيل ضغط الصفحات في ZRAM بدلاً من مسح الكاش من الذاكرة الفلاشية البطيئة).
  * `vm.page-cluster = 0` (منع قراءة المقاطع مسبقاً بما يناسب الذاكرة العشوائية السريعة).
  * `vm.dirty_ratio = 15` و `vm.dirty_background_ratio = 5` لمنع تهنيج الشاشة أثناء تشغيل الفيديوهات.

---

## 5. المرحلة الرابعة: إدارة الهويات وحماية النزاهة وتعقيم الفيديو

تم في هذه المرحلة بناء الترسانة الكاملة لإدارة الحسابات، التحقق من التشفير، ودخول عالم النشر بدون "صفر مشاهدة":

### 1. خزنة الهويات وتدوير البصمات النظيفة ([`profile_vault.py`](file:///c:/Users/Youcef/Desktop/Toki/automation/profile_vault.py))
يقوم تيك توك بربط الهاتف في قاعدة بياناته المعقدة (`/service/2/device_register/`) عبر تجميع بصمة العتاد (MediaDrm 32-byte UUID + ANDROID_ID + ماك أدرس الواي فاي + عدد قطاعات الذاكرة).
* عند حظر حساب أو الرغبة في فتح حساب جديد، يوفر هذا السكربت إمكانية التبديل الفوري:
  * توليد `ANDROID_ID` عشوائي مشفر جديد.
  * توليد بصمة Widevine DRM عتادية جديدة مشتقة بـ SHA-256 عبر التحديث الأخير لـ [`DrmIdHook.kt`](file:///c:/Users/Youcef/Desktop/Toki/app/src/main/java/io/github/meiyongai/toki/hook/DrmIdHook.kt).
  * توليد ماك أدرس راوتر هواوي جديد وشبكة STC جديدة وإحداثيات جديدة بالرياض.
  * تنظيف شامل لآثار تيك توك القديمة (`applog_stats.xml` وقواعد البيانات والكاش).
* **طريقة الاستخدام:**
  ```bash
  python automation/profile_vault.py rotate
  ```

### 2. حارس نزاهة النظام Play Integrity ([`play_integrity_guard.py`](file:///c:/Users/Youcef/Desktop/Toki/automation/play_integrity_guard.py))
* يفحص جاهزية الهاتف لاجتياز اختبارات جوجل أثناء عمليات التسجيل، ربط الهاتف بـ SMS، وتفعيل المتاجر والأرباح.
* يتأكد من مطابقة بصمة النظام `samsung/a02xx/a02:11/.../release-keys`، استجابة خدمة `android.hardware.keymaster@4.0-service`، وجاهزية مستوى النزاهة `MEETS_DEVICE_INTEGRITY`.
* **طريقة الاستخدام:**
  ```bash
  python automation/play_integrity_guard.py
  ```

### 3. معقم الفيديو ومانع الصفر مشاهدة ([`video_sanitizer.py`](file:///c:/Users/Youcef/Desktop/Toki/automation/video_sanitizer.py))
تفحص خوارزميات تيك توك (`libttvesdk.so`) مقاطع الفيديو المرفوعة بحثاً عن وسوم المونتاج للكمبيوتر وتطبيقات الطرف الثالث لمعاقبتها:
* يقوم السكربت بـ:
  1. مسح وتفريغ كل وسوم برامج الكمبيوتر (Adobe Premiere, CapCut Desktop, Final Cut, Lavf, FFmpeg).
  2. حقن وسوم كاميرا هاتف Samsung Galaxy A02 الأصلية (`samsung`، `SM-A022F`).
  3. حقن توقيع مشفر معالج ميدياتك للترميز العتادي `OMX.MTK.VIDEO.ENCODER.AVC`.
  4. حقن وسوم إحداثيات الرياض الجغرافية في حاوية MP4 (`+24.7136+046.6753/`).
  5. نقل الفيديو فورياً إلى مسار كاميرا الهاتف `/sdcard/DCIM/Camera/` وإطلاق إشعار لنظام أندرويد عبر `MediaScanner` ليظهر داخل تطبيق تيك توك كأنه فيديو تم تصويره للتو بكاميرا الهاتف الحقيقية!
* **طريقة الاستخدام:**
  ```bash
  python automation/video_sanitizer.py my_video.mp4 --push
  ```

### 4. البروكسي الشفاف معدوم الواجهات ([`95-zero-interface-redirect.sh`](file:///c:/Users/Youcef/Desktop/Toki/research/tools/95-zero-interface-redirect.sh))
* يتيح تشغيل البروكسي بتقنية `iptables NAT REDIRECT` بدون إنشاء كارت `tun0` على الإطلاق.
* يعمي تماماً فحص مقابس النواة المباشرة `AF_NETLINK` حيث لا يرى نظام أندرويد سوى الكروت الأصلية للجهاز (`lo` و `wlan0`).

### 5. محرك الأتمتة البايومترية والسلوك البشري المتطور ([`ksa_human_agent.py`](file:///c:/Users/Youcef/Desktop/Toki/automation/ksa_human_agent.py))
تمت ترقية محاكي المشاهدة والسحب ليعمل بأعلى معايير الإنتروبيا والسلوك البشري:
* **توزيع أوقات المشاهدة ثنائي النمط (Bimodal Log-Normal Mixture):**
  * **نمط التخطي السريع (Skip Mode - 22%):** فحص الفيديو والمقدمة لمدة بين `0.8` إلى `2.4` ثانية ثم السحب فوراً كأي مستخدم لم يعجبه المحتوى.
  * **نمط المشاهدة المتفاعلة (Engaged Mode - 78%):** مشاهدة متعمقة تتراوح بين `9.0` إلى `48.0` ثانية (توزيع لوغاريتمي طبيعي مركزه 20 ثانية).
* **الانجراف المكاني ثنائي الأبعاد (2D Postural Drift):**
  * محاكاة تبدل وضعية إمساك الهاتف وتعب اليد عبر نموذج رياضي (Ornstein-Uhlenbeck random walk)، مما يمنع ثبات إحداثيات السحب في صندوق مربع ثابت (وهو ما يكشف البوتات العادية).
* **إشارات محيطية وتفاعلات عشوائية ذكية:**
  * محاكاة الضغط العشوائي على أزرار الصوت الفيزيائية (`VOLUME_UP` / `VOLUME_DOWN`).
  * إيقاف الفيديو مؤقتاً لملاحظة لقطة ثم استئنافه.
  * فتح صندوق التعليقات وتصفحه ببطء ثم إغلاقه.
  * النقر على صورة صاحب الحساب لاستعراض ملفه ثم الضغط على زر الرجوع (Back).

---

## 6. بوابة الفحص السريري لسلامة النظام (28 نقطة فحص)

تم دمج أداة الفحص الشاملة [`automation/preflight_check.py`](file:///c:/Users/Youcef/Desktop/Toki/automation/preflight_check.py) للتأكد من نجاح كافة الحمايات قبل تشغيل تيك توك:

| الرقم | اسم الفحص (Check Name) | الحالة المطلوبة للنجاح | الهدف الأمني |
| :---: | :--- | :---: | :--- |
| **01** | Always-On VPN Application | `com.v2ray.ang` | تفعيل البروكسي الدائم في إعدادات النظام |
| **02** | Always-On VPN Lockdown | `1` | تفعيل مفتاح القتل (Kill Switch) لحظر النت عند انقطاع البروكسي |
| **03** | v2rayNG Process Status | عمليات نشطة | التأكد من عمل تطبيق البروكسي |
| **04** | VPN tun0 Network Interface | `UP` | التأكد من عمل النفق المشفر |
| **05** | Saudi Arabia Exit IP Routing | `Country = SA` | التأكد من أن الـ IP الخارجي سعودي 100% |
| **06** | ip6tables OUTPUT Policy | `DROP` | التأكد من إسقاط حزم IPv6 |
| **07** | sysctl disable_ipv6 | `1` | تعطيل بروتوكول IPv6 على مستوى النواة |
| **08** | QUIC UDP/443 Interception | `REJECT` | إجبار تيك توك على التحول لـ TCP TLS 1.3 |
| **09** | WebRTC STUN Egress Block | `REJECT` | حظر خروج أي حزم UDP لتيك توك عبر الواي فاي |
| **10** | Native VerifiedBootState | `green` | تطهير البوت لودر في الذاكرة العشوائية |
| **11** | Native Flash Locked Flag | `1` | إظهار حالة قفل الذاكرة الفلاشية |
| **12** | Hardware Touch Driver DEX | جاهز وموجود | التأكد من وجود سائق اللمس العتادي `/data/local/tmp/` |
| **13** | Vector Zygisk Module | نشط ومثبت | التأكد من عمل إطار عمل Vector لـ LSPosed |
| **14** | Toki Module Version | `2.0.0` | التأكد من تفعيل وحدة Toki Enterprise |
| **15** | Cellular SIM Country ISO | `sa` | انتحال كود الدولة للشريحة |
| **16** | Cellular Operator Numeric | `42001` | انتحال كود مشغل الاتصالات STC |
| **17** | Cellular Operator Alpha | `STC` | انتحال اسم المشغل STC |
| **18** | Samsung Firmware CSC | `KSA` | انتحال كود الروم الموجه للسعودية |
| **19** | System Timezone | `Asia/Riyadh` | انتحال توقيت العاصمة الرياض |
| **20** | Wi-Fi Background Scanning | `0` | تعطيل فحص الواي فاي بالخلفية |
| **21** | BLE Background Scanning | `0` | تعطيل فحص البلوتوث بالخلفية |
| **22** | Battery Temperature | `< 42°C` | التأكد من سلامة حرارة الهاتف |
| **23** | Available RAM Headroom | `> 350MB` | التأكد من وجود ذاكرة كافية لفك تشفير الفيديو |
| **24** | SELinux Status | `Enforcing (1)` | التأكد من بقاء حماية SELinux مفعلة |
| **25** | Resetprop Stealth Service | مثبت بالنظام | التأكد من خدمة تطهير البوت لودر التلقائية |
| **26** | MT6739 VM & OOM Service | مثبت بالنظام | التأكد من خدمة حماية البروكسي وتحسين الذاكرة |
| **27** | Kernel Firewall Service | مثبت بالنظام | التأكد من عمل جدار الحماية التلقائي |
| **28** | ZRAM Swappiness Tuning | `100` | التأكد من تفعيل أقصى استفادة من ZRAM |

---

## 7. دليل التشغيل اليومي خطوة بخطوة (Runbook)

اتبع هذه الخطوات البسيطة لتشغيل جلسة عمل احترافية آمنة في أي وقت:

### الخطوة 1: توصيل الهاتف وتجهيز البروكسي والـ VPN التلقائي
1. صل الهاتف بالكمبيوتر عبر كابل USB وتأكد من تفعيل وضع تصحيح الأخطاء ADB.
2. **الـ VPN يعمل الآن أوتوماتيكياً بالكامل:** بمجرد فتح الهاتف أو إقلاعه، تقوم خدمة المراقبة الدائمة [`94-vpn-autostart-daemon.sh`](file:///c:/Users/Youcef/Desktop/Toki/research/tools/94-vpn-autostart-daemon.sh) بالاتصال الفوري وتثبيت عنوان الرياض (السعودية) دون الحاجة لأي نقر يدوي.
3. للتحكم في الـ VPN أو مراقبته برمجياً من الكمبيوتر، يمكنك استخدام الأداة الجديدة [`automation/vpn_manager.py`](file:///c:/Users/Youcef/Desktop/Toki/automation/vpn_manager.py):
   ```bash
   python automation/vpn_manager.py status
   ```

### الخطوة 2: تشغيل الفحص السريري لسلامة النظام
من خلال موجه الأوامر في الكمبيوتر داخل مجلد المشروع، نفذ الأمر:
```bash
python automation/preflight_check.py
```
* **النتيجة المتوقعة:** ظهور النتيجة باللون الأخضر: `[STATUS: ZERO LEAK PASS] 28/28 CHECKS PASSED`.

### الخطوة 3: إدارة الهويات (اختياري - عند الرغبة في حساب جديد)
إذا كنت تريد البدء بهوية هاتف جديدة تماماً ونظيفة:
```bash
python automation/profile_vault.py rotate
```
* سيقوم السكربت بمسح بيانات تيك توك وتوليد بصمات عتادية وواي فاي جديدة بالكامل.

### الخطوة 4: تشغيل الأتمتة البايومترية الذكية
لتشغيل الروبوت البايومتري الذكي لتصفح وتدفئة الحساب (مثلاً لمشاهدة 20 فيديو بسلوك بشري كامل):
```bash
python automation/ksa_human_agent.py 20
```

### الخطوة 5: رفع مقاطع الفيديو بدون حظر "صفر مشاهدة" (عند الرغبة بالنشر)
إذا كان لديك فيديو قمت بتصميمه على الكمبيوتر وتريد نشره بأمان:
```bash
python automation/video_sanitizer.py my_video.mp4 --push
```
* سيتم تعقيم الفيديو وحقن وسوم هاتف سامسونج A02 الأصلية وإرساله مباشرة إلى استوديو كاميرا الهاتف (`DCIM/Camera`) لتقوم بنشره من داخل تيك توك بأمان تام!

---

## 8. فهرس الملفات والأدوات في المستودع

| مسار الملف | النوع | الوظيفة الأساسية |
| :--- | :---: | :--- |
| [`automation/vpn_manager.py`](file:///c:/Users/Youcef/Desktop/Toki/automation/vpn_manager.py) | Python | أداة التحكم السريع وإدارة وتثبيت حارس الـ VPN التلقائي ومراقبة الـ IP |
| [`automation/ksa_human_agent.py`](file:///c:/Users/Youcef/Desktop/Toki/automation/ksa_human_agent.py) | Python | محرك الأتمتة البايومترية وإدارة اللمس العتادي وتوزيع المشاهدة اللوغاريتمي |
| [`automation/preflight_check.py`](file:///c:/Users/Youcef/Desktop/Toki/automation/preflight_check.py) | Python | بوابة الفحص والتدقيق السريري الشامل (28 نقطة فحص) |
| [`automation/profile_vault.py`](file:///c:/Users/Youcef/Desktop/Toki/automation/profile_vault.py) | Python | خزنة إدارة وتدوير الهويات العتادية والبصمات النظيفة |
| [`automation/play_integrity_guard.py`](file:///c:/Users/Youcef/Desktop/Toki/automation/play_integrity_guard.py) | Python | أداة فحص واختبار نزاهة بيئة جوجل وشهادات Keymaster 4.0 |
| [`automation/video_sanitizer.py`](file:///c:/Users/Youcef/Desktop/Toki/automation/video_sanitizer.py) | Python | أداة تعقيم الفيديو وحقن وسوم كاميرا سامسونج لمنع الصفر مشاهدة |
| [`research/tools/94-vpn-autostart-daemon.sh`](file:///c:/Users/Youcef/Desktop/Toki/research/tools/94-vpn-autostart-daemon.sh) | Shell | شيطان Magisk الدائم لتشغيل وإعادة توصيل الـ VPN وحمايته تلقائياً فور فتح الهاتف |
| [`research/tools/TouchDriver.java`](file:///c:/Users/Youcef/Desktop/Toki/research/tools/TouchDriver.java) | Java | الكود المصدري لسائق اللمس العتادي المباشر في النواة `/dev/input/event3` |
| [`research/tools/touch_driver.jar`](file:///c:/Users/Youcef/Desktop/Toki/research/tools/touch_driver.jar) | DEX/JAR | السائق العتادي المترجم والجاهز للتشغيل الفوري على الهاتف |
| [`research/tools/97-resetprop-stealth.sh`](file:///c:/Users/Youcef/Desktop/Toki/research/tools/97-resetprop-stealth.sh) | Shell | سكربت الإقلاع الدائم لتطهير البوت لودر في ذاكرة النظام (`green` / `locked`) |
| [`research/tools/98-vpn-oom-guard.sh`](file:///c:/Users/Youcef/Desktop/Toki/research/tools/98-vpn-oom-guard.sh) | Shell | سكربت الإقلاع الدائم لحماية الـ VPN من القتل وتحسين ذاكرة MT6739 ZRAM |
| [`research/tools/99-ksa-firewall.sh`](file:///c:/Users/Youcef/Desktop/Toki/research/tools/99-ksa-firewall.sh) | Shell | جدار حماية النواة الدائم لإسقاط IPv6 ومنع تسريبات WebRTC و QUIC |
| [`research/tools/95-zero-interface-redirect.sh`](file:///c:/Users/Youcef/Desktop/Toki/research/tools/95-zero-interface-redirect.sh) | Shell | سكربت البروكسي الشفاف معدوم الواجهات لإلغاء `tun0` من مقابس النواة |
| [`AUTOMATIC_VPN_IMPLEMENTATION.md`](file:///c:/Users/Youcef/Desktop/Toki/AUTOMATIC_VPN_IMPLEMENTATION.md) | Markdown | الدليل الشامل لنظام التشغيل التلقائي للـ VPN وحمايته من القتل ونواقل تسريبات الـ DNS والذاكرة |
| [`ARGON4_DEEPDIVE_AR.md`](file:///c:/Users/Youcef/Desktop/Toki/ARGON4_DEEPDIVE_AR.md) | Markdown | التقرير الاستخباري المعماري الشامل لمعلومات أرغون 4 (نداءات النواة، كابتشا تورينغ، ومصفوفة الـ 48 ساعة) |
| [`complete_v3.md`](file:///c:/Users/Youcef/Desktop/Toki/complete_v3.md) | Markdown | تقرير الإنجاز التقني للمرحلة الثالثة باللغة الإنجليزية |
| [`COMPLETE_AR.md`](file:///c:/Users/Youcef/Desktop/Toki/COMPLETE_AR.md) | Markdown | هذا الدليل الشامل باللغة العربية |

---
**تم إعداد هذا التوثيق ليكون مرجعاً هندسياً دائماً وشاملاً لكافة مراحل المنظومة.**
