# منصة الاختبار التفاعلي — QWS

<p align="center">
  <strong>منصة اختبار محلية تفاعلية عن الأردوينو وبايثون وإنترنت الأشياء</strong>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white">
  <img alt="Flask" src="https://img.shields.io/badge/Flask-3.x-black?logo=flask&logoColor=white">
  <img alt="SQLite" src="https://img.shields.io/badge/SQLite-3-lightgrey?logo=sqlite&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green">
  <img alt="Platform" src="https://img.shields.io/badge/Platform-Local-orange">
</p>

---

## نظرة عامة

منصة اختبار تفاعلية تعمل محليًا (`localhost`) مصممة لاختبار الطلاب في موضوعات الأردوينو، بايثون، وإنترنت الأشياء. تدعم الواجهة العربية بالكامل مع تخطيط RTL، وتوفر تجربة اختبار متكاملة مع مؤقت، حفظ تلقائي، مكافحة غش، ولوحة إدارة للأسئلة والنتائج.

### المميزات الرئيسية

- **اختبار تفاعلي** — 95 سؤال اختيار من متعدد (MCQ) موزعة على أقسام متنوعة
- **مؤقت ذكي** — عد تنازلي مع حفظ الوقت المتبقي تلقائيًا
- **حفظ تلقائي** — تُحفظ إجابات الطالب تلقائيًا أثناء الاختبار
- **استئناف الاختبار** — رمز فريد يسمح للطالب باستئناف الاختبار من حيث توقف
- **مكافحة الغش** — كشف تبديل التبويبات وتعطيل النسخ واللصق
- **لوحة إدارة** — إضافة/تعديل/حذف الأسئلة مع دعم الصور
- **مراجعة الإجابات** — عرض تفصيلي لإجابات كل طالب للأدمن
- **لوحة إحصائيات** — رسوم بيانية وإحصائيات شاملة عن الأداء
- **تصدير CSV** — تصدير نتائج الطلاب إلى ملف CSV
- **حذف الطلاب** — إمكانية حذف طالب وكل تفاصيل إجاباته
- **دعم الصور** — إضافة صورة (رابط URL) لأي سؤال
- **واجهة عربية كاملة** — تصميم RTL مع دعم كامل للغة العربية

---

## التقنيات المستخدمة

| التقنية | الاستخدام |
|---------|-----------|
| **Python 3.8+** | لغة الخادم الخلفي |
| **Flask** | إطار عمل الويب الخلفي |
| **SQLite** | قاعدة بيانات النتائج وسجلات التقدم |
| **JSON** | تخزين بنك الأسئلة |
| **HTML/CSS/JS** | الواجهة الأمامية (بدون إطار عمل) |
| **Jinja2** | محرك القوالب |

---

## المتطلبات

- **Python 3.8+**
- **Flask** (المكتبة الوحيدة المطلوبة)

---

## التثبيت والتشغيل

### 1. تثبيت المكتبات

```bash
pip install -r requirements.txt
```

> **ملاحظة:** `requirements.txt` يحتوي على `flask` فقط.

### 2. تشغيل الخادم

```bash
python app.py
```

### 3. فتح المنصة

افتح المتصفح على:

```
http://localhost:5000
```

---

## بنية المشروع

```
qws/
├── app.py                    # الخادم الرئيسي (Flask)
├── content.text              # بنك الأسئلة الخام (المصدر)
├── parse_questions.py        # يحوّل content.text → questions.json
├── questions.json            # بنك الأسئلة المُولّد (95 سؤال MCQ)
├── quiz.db                   # قاعدة SQLite للنتائج وسجلات التقدم
├── results.json              # نسخة احتياطية قديمة (تُرحّل تلقائيًا)
├── requirements.txt          # flask
├── README.md                 # هذا الملف
│
├── templates/                # قوالب Jinja2 (RTL)
│   ├── base.html             # القالب الأساسي
│   ├── login.html            # تسجيل الدخول + استئناف
│   ├── quiz.html             # صفحة الاختبار
│   ├── result.html           # نتيجة الطالب
│   ├── results.html          # قائمة كل النتائج
│   ├── stats.html            # لوحة الإحصائيات
│   ├── admin.html            # لوحة الإدارة (دخول + إدارة أسئلة)
│   ├── admin_answers.html    # مراجعة إجابات الطلاب
│   └── resume_error.html     # خطأ رمز الاستئناف
│
├── static/
│   ├── script.js             # منطق الواجهة (مؤقت، حفظ، مكافحة غش)
│   ├── style.css             # الأنماط الرئيسية
│   └── css/                  # أنماط منفصلة لكل صفحة
│       ├── variables.css     # متغيرات CSS (ألوان، خطوط)
│       ├── base.css          # الأنماط الأساسية
│       ├── components.css    # المكونات المشتركة
│       ├── quiz.css          # أنماط صفحة الاختبار
│       ├── result.css        # أنماط صفحة النتيجة
│       ├── resume.css        # أنماط صفحة الاستئناف
│       ├── stats.css         # أنماط لوحة الإحصائيات
│       ├── admin.css         # أنماط لوحة الإدارة
│       └── responsive.css    # التجاوب مع الشاشات
│
└── openspec/                 # مواصفات المشروع
    ├── config.yaml           # إعدادات OpenSpec
    ├── specs/                # مواصفات القدرات (8 قدرات)
    └── changes/              # تغييرات قيد التقدم + archive/
```

---

## المسارات (Routes)

| المسار | الطريقة | الوصف |
|--------|---------|-------|
| `/` | GET, POST | تسجيل دخول الطالب + استئناف |
| `/quiz` | GET | صفحة الاختبار |
| `/save` | POST | حفظ تلقائي للإجابات |
| `/submit` | POST | تسليم الاختبار والتصحيح |
| `/result` | GET | عرض نتيجة الطالب |
| `/results` | GET | قائمة كل النتائج |
| `/export` | GET | تصدير النتائج إلى CSV |
| `/stats` | GET | لوحة الإحصائيات |
| `/resume/<code>` | GET | استئناف الاختبار برمز |
| `/logout` | GET | خروج الطالب |
| `/admin` | GET, POST | دخول الإدارة |
| `/admin/questions` | GET | إدارة الأسئلة |
| `/admin/questions/add` | POST | إضافة سؤال |
| `/admin/questions/<id>/edit` | GET, POST | تعديل سؤال |
| `/admin/questions/<id>/delete` | POST | حذف سؤال |
| `/admin/answers` | GET | مراجعة إجابات الطلاب |
| `/admin/answers/detail` | GET | تفاصيل إجابة طالب |
| `/admin/answers/delete` | POST | حذف طالب |
| `/admin/logout` | GET | خروج الإدارة |

---

## قاعدة البيانات

### جدول `results`

يخزن نتائج الطلاب وسجلات التقدم.

| الحقل | النوع | الوصف |
|-------|------|-------|
| `id` | INTEGER PK | معرف فريد |
| `name` | TEXT | اسم الطالب |
| `status` | TEXT | `completed` أو `in_progress` |
| `resume_code` | TEXT | رمز استئناف فريد |
| `answers` | TEXT | إجابات الطالب (JSON) |
| `remaining_seconds` | INTEGER | الوقت المتبقي |
| `started_at` | TEXT | وقت البدء |
| `correct` | INTEGER | عدد الإجابات الصحيحة |
| `total` | INTEGER | إجمالي الأسئلة |
| `percentage` | REAL | النسبة المئوية |
| `date` | TEXT | تاريخ الاختبار |
| `time_spent_seconds` | INTEGER | الوقت المستغرق |
| `tab_switches` | INTEGER | عدد تبديل التبويبات |
| `wrong_question_ids` | TEXT | معرفات الأسئلة الخاطئة |

### جدول `answer_details`

يخزن تفاصيل إجابات كل سؤال لكل طالب (للأدمن فقط).

| الحقل | النوع | الوصف |
|-------|------|-------|
| `id` | INTEGER PK | معرف فريد |
| `student_name` | TEXT | اسم الطالب |
| `question_id` | INTEGER | معرف السؤال |
| `section` | TEXT | القسم |
| `question_text` | TEXT | نص السؤال |
| `code` | TEXT | الكود البرمجي (إن وُجد) |
| `image` | TEXT | رابط الصورة (إن وُجد) |
| `user_answer` | TEXT | إجابة الطالب |
| `correct_answer` | TEXT | الإجابة الصحيحة |
| `correct_text` | TEXT | نص الإجابة الصحيحة |
| `is_correct` | INTEGER | 1 صحيحة، 0 خاطئة |
| `date` | TEXT | تاريخ الاختبار |

---

## إعادة توليد بنك الأسئلة

لتوليد `questions.json` من `content.text`:

```bash
python parse_questions.py
```

يطبع عدد الأسئلة المُولّدة (95) وملخص الأقسام ويعيد كتابة `questions.json`.

> **ملاحظة:** اضبط `PYTHONIOENCODING=utf-8` قبل التشغيل على Windows:
> ```powershell
> $env:PYTHONIOENCODING="utf-8"
> python parse_questions.py
> ```

---

## لوحة الإدارة

- **الدخول:** `http://localhost:5000/admin`
- **كلمة المرور الافتراضية:** `admin123`

### ما يمكنك فعله:

- **إدارة الأسئلة** — إضافة، تعديل، حذف الأسئلة مع دعم الصور والكود البرمجي
- **مراجعة الإجابات** — عرض تفصيلي لإجابات كل طالب
- **حذف الطلاب** — حذف طالب وكل تفاصيل إجاباته
- **الإحصائيات** — لوحة شاملة مع رسوم بيانية
- **تصدير CSV** — تصدير نتائج جميع الطلاب

---

## مكافحة الغش

- **كشف تبديل التبويبات** — يُسجل عدد مرات تبديل التبويب أثناء الاختبار
- **تعطيل النسخ واللصق** — يمنع نسخ الأسئلة أو لصق إجابات
- **حفظ تلقائي** — تُحفظ الإجابات تلقائيًا كل بضع ثوانٍ

---

## الترخيص

هذا المشروع مرخص تحت رخصة MIT.
