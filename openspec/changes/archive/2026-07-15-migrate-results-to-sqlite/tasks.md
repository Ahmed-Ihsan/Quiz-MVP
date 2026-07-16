## 1. تحديث القيود والمواصفات

- [x] 1.1 تحديث `AGENTS.md`: إسقاط قيد "بدون قاعدة بيانات" وتحديث قسم التقنيات والتخزين ليشمل SQLite لنتائج المستخدمين
- [x] 1.2 تحديث `openspec/config.yaml`: تغيير سطر التخزين في `context` من "ملفات JSON (بدون قاعدة بيانات)" إلى "SQLite لنتائج المستخدمين + JSON للأسئلة"
- [x] 1.3 التحقق: `openspec validate migrate-results-to-sqlite` ينجح

## 2. تنفيذ طبقة تخزين SQLite في app.py

- [x] 2.1 إضافة `import sqlite3` و `DB_FILE = os.path.join(BASE_DIR, "quiz.db")`
- [x] 2.2 كتابة `init_db()`: إنشاء الجدول `CREATE TABLE IF NOT EXISTS results` + ترحيل `results.json` إن وُجد والجدول فارغ
- [x] 2.3 كتابة `_row_to_dict(row)`: تحويل صف SQLite إلى قاموس مع `setdefault` للتوافق العكسي وتفكيك حقول JSON
- [x] 2.4 إعادة كتابة `load_results()`: SELECT * من الجدول، إرجاع قائمة قواميس
- [x] 2.5 إعادة كتابة `save_results(results)`: حذف كامل الجدول + إعادة إدراج ضمن معاملة ذرية واحدة
- [x] 2.6 إعادة كتابة `generate_resume_code()`: SELECT resume_codes الموجودة للتحقق من التفرّد
- [x] 2.7 إعادة كتابة `find_in_progress(name)`: SELECT WHERE status='in_progress' AND name=? ORDER BY started_at DESC LIMIT 1
- [x] 2.8 إعادة كتابة `find_by_resume_code(code)`: SELECT WHERE UPPER(resume_code)=?
- [x] 2.9 إعادة كتابة `upsert_progress(record)`: INSERT OR REPLACE بحسب resume_code
- [x] 2.10 استدعاء `init_db()` على مستوى الوحدة قبل المسارات
- [x] 2.11 التحقق: التطبيق يبدو بدون أخطاء استيراد — `python -c "import app"`

## 3. التحقق الوظيفي الكامل

- [x] 3.1 تشغيل الخادم والتأكد من إنشاء `quiz.db` تلقائيًا
- [x] 3.2 اختبار تسجيل الدخول وبدء اختبار جديد (إنشاء سجل in_progress)
- [x] 3.3 اختبار الحفظ التلقائي (/save) لتحديث الإجابات
- [x] 3.4 اختبار إرسال الاختبار (/submit) وتحويل السجل إلى completed
- [x] 3.5 اختبار صفحة /results تعرض النتائج المكتملة
- [x] 3.6 اختبار /export يُنزّل CSV صحيح
- [x] 3.7 اختبار /stats يحسب الإحصائيات
- [x] 3.8 اختبار الاستئناف برمز صالح ورمز غير صالح
- [x] 3.9 التحقق من ترحيل results.json الحالي عند أول تشغيل

## 4. التحقق النهائي والأرشفة

- [x] 4.1 `openspec validate --all` ينجح
- [x] 4.2 `openspec status --change migrate-results-to-sqlite` يُظهر اكتمال كل العناصر
- [x] 4.3 `openspec archive migrate-results-to-sqlite`
