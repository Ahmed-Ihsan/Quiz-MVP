# مهام تحسين UI/UX المتقدم

## المرحلة 1: نظام التصميم التأسيسي

- [x] 1.1 إنشاء `templates/base.html` — قالب أساس مشترك (Google Fonts Cairo, dark-mode inline script, meta tags, RTL)
- [x] 1.2 إعادة كتابة `static/style.css` — نظام CSS Custom Properties (ألوان، ظلال، مسافات، أنصاف أقطار، انتقالات) للوضعين النهاري والليلي
- [x] 1.3 إضافة reset عربي (line-height 1.75, letter-spacing 0, logical properties, text-align: start)
- [x] 1.4 إضافة `@media (prefers-reduced-motion: reduce)` لتعطيل الحركات
- [x] 1.5 تحقق: فتح style.css والتأكد من وجود متغيرات الوضعين + reduced-motion

## المرحلة 2: صفحة الاختبار — البنية

- [x] 2.1 تحديث `templates/quiz.html` ليرث من `base.html`
- [x] 2.2 إعادة تصميم رأس الصفحة (glassmorphism, شريط تقدم بتدرج, زر dark mode, زر ملء شاشة بأيقونة, avatar الطالب)
- [x] 2.3 إعادة تصميم بطاقات الأسئلة (شارة رقم دائرية, ظلال طبقية, كتل كود editor-style)
- [x] 2.4 إعادة تصميم الخيارات (راديو مخصص, تأكيد بصري, hover/focus states)
- [x] 2.5 إعادة تصميم صندوق رمز الاستئناف (زر نسخ, تصميم أنظف)
- [x] 2.6 إعادة تصميم زر الإرسال (حالة loading, تعطيل مزدوج)
- [x] 2.7 تحقق: فتح quiz.html والتأكد من البنية الجديدة + وراثة base.html

## المرحلة 3: صفحة الاختبار — JavaScript

- [x] 3.1 إضافة نظام toast notifications (عنصر منزلق, auto-dismiss, ARIA)
- [x] 3.2 إضافة مودال مخصص لاستبدال confirm() (أسئلة غير مُجابة)
- [x] 3.3 إضافة تبديل الوضع الليلي (زر, localStorage, prefers-color-scheme)
- [x] 3.4 إضافة التنقل بلوحة المفاتيح للخيارات (أسهم أعلى/أسفل)
- [x] 3.5 إضافة IntersectionObserver للظهور التدريجي لبطاقات الأسئلة
- [x] 3.6 إضافة حالة loading لزر الإرسال (spinner + تعطيل)
- [x] 3.7 إضافة زر نسخ لرمز الاستئناف (clipboard API + تأكيد بصري)
- [x] 3.8 استبدال alert() بـ toast في كشف تبديل التبويب
- [x] 3.9 تحقق: فتح script.js والتأكد من عدم وجود alert()/confirm() الأصليين

## المرحلة 4: الوصولية

- [x] 4.1 إضافة aria-label عربية على جميع الأزرار والمؤشرات في quiz.html
- [x] 4.2 إضافة role="status" + aria-live="polite" لشريط التقدم
- [x] 4.3 إضافة focus-visible styles (حلقة 3px بلون primary)
- [x] 4.4 تحقق: فحص تباين الألوان WCAG AA في الوضعين

## المرحلة 5: التحقق الشامل

- [x] 5.1 تشغيل الخادم: `python app.py` وفتح http://localhost:5000
- [x] 5.2 اختبار بصري: صفحة الاختبار في الوضع النهاري
- [x] 5.3 اختبار بصري: تبديل الوضع الليلي + إعادة التحميل (لا FOUC)
- [x] 5.4 اختبار الجوال: تصغير النافذة + فحص التجاوب
- [x] 5.5 اختبار لوحة المفاتيح: Tab + أسهم + Enter
- [x] 5.6 اختبار الإشعارات: toast عند تبديل التبويب + مودال عند الإرسال بأسئلة فارغة
- [x] 5.7 openspec validate advanced-ui-ux
- [x] 5.8 openspec validate --all
