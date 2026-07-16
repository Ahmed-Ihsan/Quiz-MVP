## Context

يخزّن التطبيق حاليًا سجلات التقدّم والنتائج في ملف `results.json` بنمط read-modify-write: تُحمَّل كل السجلات في الذاكرة، تُعدَّل، ثم تُكتَب المجموعة كاملة بالكتابة فوق الملف مباشرةً (`open(..., "w")`). هذا النمط عرضة للتلف عند المقاطعة — حدث فعلًا `JSONDecodeError: Extra data` لأن كتابة قُوطعت ولم تُكتَب فوق المحتوى القديم بالكامل.

الدوال المعنية: `load_results`, `save_results`, `generate_resume_code`, `find_in_progress`, `find_by_resume_code`, `upsert_progress`. المستدعون: `login`, `quiz`, `save`, `resume`, `submit`, `results`, `export`, `stats`.

السجل له شكلان: `in_progress` (name, status, resume_code, answers, remaining_seconds, started_at) و `completed` (name, correct, total, percentage, date, time_spent_seconds, tab_switches, wrong_question_ids, status, resume_code).

## Goals / Non-Goals

**Goals:**
- استبدال `results.json` بـ SQLite مع كتابة ذرية لمنع التلف.
- الحفاظ على نفس سلوك الواجهة والمسارات دون تغيير.
- ترحيل بيانات `results.json` الحالية تلقائيًا.
- عدم إضافة تبعيات خارجية (sqlite3 ضمن المكتبة القياسية).

**Non-Goals:**
- لا ترحيل `questions.json` — يبقى ملفًا مُولّدًا من `parse_questions.py` (مدخلات للقراءة فقط).
- لا إضافة ORM — استخدام `sqlite3` مباشرةً.
- لا مصادقة متعددة المستخدمين — يبقى المستخدم الواحد لكل محاولة.
- لا تغيير للواجهة الأمامية أو قوالب Jinja2.

## Decisions

### القرار 1: جدول واحد لكل من in_progress و completed
جدول `results` واحد بأعمدة اختيارية تغطي كلا الشكلين. عمود `status` يميّز بين `in_progress` و `completed`. الأعمدة الخاصة بكل حالة (مثل `answers`, `correct`) تكون `NULL` عند عدم الانطباق.

**البديل المُستبعَد:** جدولان منفصلان (progress + results) — يضيف تعقيدًا في الربط بين سجل التقدّم والنتيجة النهائية دون فائدة فعلية، ويتطلب منطق ترحيل للسجل الواحد.

### القرار 2: تخزين الحقول المركّبة (answers, wrong_question_ids) كنص JSON
عمود `answers` يخزّن `{"q1": "أ", ...}` كنص JSON، و `wrong_question_ids` يخزّن `[1, 5, 12]` كنص JSON. تُفسَّر عند القراءة وتُسلسَل عند الكتابة.

**البديل المُستبعَد:** جدول منفصل للإجابات (question_id, answer) — مبالغة في التصميم لتطبيق محلي بسيط بمستخدم واحد.

### القرار 3: دوال بنفس التوقيعات الحالية
إبقاء `load_results()` تُرجع قائمة قواميس، و `find_*` و `upsert_progress` بنفس التوقيعات. هذا يقلّل التغييرات في المستدعين (المسارات) إلى الحد الأدنى. تُعاد كتابة `save_results()` لقبول قائمة كاملة (للتوافق مع `login` و `submit` اللذين يستخدمان read-modify-write) عبر حذف كامل الجدول وإعادة الإدراج ضمن معاملة واحدة ذرية.

**البديل المُستبعَد:** إعادة هيكلة كاملة للمستدعين لاستخدام عمليات SQLite مستهدفة — تغيير كبير غير ضروري، والسلوك الوظيفي لا يتغير.

### القرار 4: ترحيل لمرة واحدة عند أول تشغيل
عند بدء التطبيق، إذا كان جدول `results` فارغًا وملف `results.json` موجود، تُستورد السجلات إلى SQLite. لا يُحذف `results.json` (يُترك كنسخة احتياطية).

### القرار 5: init_db() عند الاستيراد
استدعاء `init_db()` على مستوى الوحدة عند استيراد `app.py`، قبل استقبال أي طلب. هذا يضمن وجود الجدول دائمًا.

مخطط الجدول:
```sql
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'completed',
    resume_code TEXT UNIQUE,
    answers TEXT,
    remaining_seconds INTEGER,
    started_at TEXT,
    correct INTEGER,
    total INTEGER,
    percentage REAL,
    date TEXT,
    time_spent_seconds INTEGER DEFAULT 0,
    tab_switches INTEGER DEFAULT 0,
    wrong_question_ids TEXT
);
```

## Risks / Trade-offs

- [فقدان ملف quiz.db] → التطبيق ينشئ قاعدة جديدة فارغة تلقائيًا؛ يُنصح بنسخ `results.json` الاحتياطية. الخطر منخفض (تطبيق محلي).
- [تعارض resume_code فريد] → القيد `UNIQUE` على `resume_code` يمنع التكرار على مستوى قاعدة البيانات؛ `generate_resume_code` يتحقق من التفرّد قبل الإدراج.
- [توافق السجلات القديمة بدون status] → طبقة القراءة تطبّق `setdefault("status", "completed")` كما في الكود الحالي.
- [ترحيل ملف results.json تالف] → دالة الترحيل تتسامح مع الأخطاء: إذا فشل `json.load`، تُسجَّل تحذير وتُتجاوز الترحيل (تبدأ بقاعدة فارغة) بدل تعطيل التطبيق.

## Migration Plan

1. عند أول تشغيل بعد التحديث: `init_db()` ينشئ `quiz.db` + الجدول.
2. إذا الجدول فارغ و `results.json` موجود وصالح: استيراد السجلات.
3. `results.json` يُترك في مكانه كنسخة احتياطية (لا يُحذف تلقائيًا).
4. التراجع: حذف `quiz.db` واستعادة `results.json` + نسخة `app.py` القديمة.
