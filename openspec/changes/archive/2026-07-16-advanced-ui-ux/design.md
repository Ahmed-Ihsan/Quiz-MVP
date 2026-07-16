# تصميم تحسين UI/UX المتقدم

## قرارات التصميم

### لماذا CSS Custom Properties بدل preprocessor؟
المشروع محلي بسيط بدون build step (لا CI/lint/format حسب AGENTS.md). CSS Custom Properties
مدعومة أصلياً في جميع المتصفحات الحديثة ولا تتطلب تجميع. هذا يتوافق مع قيد "لا framework".

### لماذا Cairo بدل Tajawal أو IBM Plex Sans Arabic؟
- Cairo: الأكثر شيوعاً للعربية على Google Fonts، أوزان متعددة (400/600/700)، مظهر حديث
- Tajawal: بديل ممتاز لكن أقل أوزان متاحة
- IBM Plex Sans Arabic: ممتاز لكن مظهر أكثر تقنية
- القرار: Cairo كافتراضي (يتوافق مع "حديث وأنيق")

### لماذا inline script في head لمنع FOUC؟
بدون inline script، يُحمّل CSS أولاً بالوضع النهاري ثم يتبدل بعد تحميل JS. هذا يسبب
وميضاً (FOUC). سكريبت inline صغير في `<head>` يقرأ localStorage ويضبط `data-theme` قبل
رندر CSS. هذا نمط قياسي مُتبع في جميع تطبيقات dark mode.

### لماذا IntersectionObserver للظهور التدريجي؟
بدل إطار عمل، IntersectionObserver API أصلي ومدعوم في جميع المتصفحات الحديثة. يُفعّل
`fade-in-up` فقط عندما تدخل البطاقة في الـ viewport. مع `prefers-reduced-motion` يُعطّل.

### لماذا toast/modal بدل alert/confirm؟
- `alert()` و`confirm()` أصليان للمتصفح، لا يدعمان RTL بشكل كامل، لا يمكن تنسيقهما،
  ويقطعان التدفق. toast وmodal مخصصان يوفران: تنسيق كامل، RTL صحيح، وصولية (ARIA)،
  وتجربة مستخدم أفضل.

## البدائل المُعتبرة والمرفوضة
1. **Tailwind CSS:** مرفوض — يتطلب build step، ينتهك قيد "لا framework"
2. **مكتبة أنميشن (GSAP/Anime.js):** مرفوضة — CSS خالص كافٍ للتفاعلات المطلوبة
3. **نظام تصميم منفصل (design-tokens.json):** مرفوض — YAGNI، CSS Custom Properties كافية
4. **Service Worker للخطوط:** مرفوض — مبالغة لمشروع محلي بسيط

## المخاطر والتخفيف
| الخطر | التخفيف |
|-------|---------|
| FOUC في الوضع الليلي | inline script في `<head>` |
| بطء تحميل الخط | `font-display: swap` + preconnect |
| تكسر قوالب Jinja2 الموجودة | قالب base.html جديد + وراثة Jinja2 |
| تباين الوصولية في الوضع الليلي | اختبار تباين WCAG AA لكل لون |
| تعارض مع مكافحة الغش | لا تغيير في منطق الكشف، فقط عرض الإشعار |

## ترتيب التنفيذ
1. قالب base.html (أساس مشترك: font link, dark-mode script, meta)
2. style.css (نظام تصميم كامل: variables, reset, components, dark mode)
3. quiz.html (تحديث البنية لاستخدام base.html + العناصر الجديدة)
4. script.js (toast, modal, dark-mode toggle, keyboard nav, IntersectionObserver, loading state)
5. التحقق: تشغيل الخادم + فحص بصري + اختبار الوضعين + اختبار الوصولية
