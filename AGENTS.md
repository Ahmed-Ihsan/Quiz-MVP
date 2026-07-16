# AGENTS.md — إرشادات الوكلاء الذكيين لمشروع qws

> ملف إرشادات موحّد لأي وكيل ذكي يعمل في هذا المستودع. اقرأه أولًا قبل أي تعديل.
> المحتوى مستمد من الكود الفعلي ومُتحقَّق منه (انظر سير عمل OpenSpec في الأسفل).

## نظرة عامة

- **الغرض:** منصة اختبار تفاعلي محلية (local) عن الأردوينو وبايثون وإنترنت الأشياء.
- **اللغة:** كل المحتوى والواجهة باللغة العربية مع دعم RTL كامل.
- **التقنيات:**
  - Backend: Python Flask
  - Frontend: HTML + CSS + JavaScript عادي (بدون framework)
  - التخزين: SQLite لنتائج المستخدمين وسجلات التقدّم (`quiz.db`)، JSON للأسئلة (`questions.json` مُولّد من `content.text`)
- **مصدر الأسئلة:** ملف `content.text` يحتوي على بنك أسئلة بالعربية (MCQ + أسئلة عملية). النطاق: أسئلة اختيارات (MCQ) فقط — تُستبعَد الأسئلة العملية (أخطاء التوصيل + تصميم مشروع).
- **عدد الأسئلة:** 95 سؤالًا (مُولّدة في `questions.json`).
- **القيود:**
  - يعمل محليًا على `http://localhost:5000`
  - بسيط وخفيف بدون تعقيد، مستخدم واحد لكل محاولة
  - كل النصوص بالعربية

## الأوامر

> المترجم المثبّت: **Python 3.8.0** على المسار:
> `C:\Users\demha\AppData\Local\Programs\Python\Python38-32\python.exe`
>
> استخدم هذا المترجم بالتحديد (لا تستخدم `python` مجردًا فقد يشير إلى إصدار آخر).
> النظام: Windows / PowerShell — استخدم `;` لفصل الأوامر لا `&&`.

### تثبيت المكتبات
```powershell
C:\Users\demha\AppData\Local\Programs\Python\Python38-32\python.exe -m pip install -r requirements.txt
```
`requirements.txt` يحتوي على `flask` فقط.

### تشغيل الخادم
```powershell
C:\Users\demha\AppData\Local\Programs\Python\Python38-32\python.exe app.py
```
ثم افتح `http://localhost:5000` في المتصفح.

### إعادة توليد بنك الأسئلة (من `content.text` إلى `questions.json`)
```powershell
$env:PYTHONIOENCODING="utf-8"
C:\Users\demha\AppData\Local\Programs\Python\Python38-32\python.exe parse_questions.py
```
يطبع عدد الأسئلة المُولّدة (95) وملخص الأقسام ويعيد كتابة `questions.json`.
> ملاحظة: اضبط `PYTHONIOENCODING=utf-8` قبل التشغيل، وإلا سيفشل طباعة أسماء الأقسام
> العربية على وحدة تحكم Windows الافتراضية (cp1252) — رغم أن `questions.json` يُكتَب
> بنجاح قبل ذلك. `questions.json` يُكتَب دائمًا بترميز UTF-8.

### التحقق من OpenSpec
```powershell
openspec validate --all
openspec list
openspec status --change <change-name>
```

## الاصطلاحات

- **اللغة والاتجاه:** كل النصوص والتعليقات بالعربية. كل قوالب HTML تبدأ بـ
  `<html lang="ar" dir="rtl">` — أي قالب جديد يجب أن يحترم RTL.
- **التخزين:** نتائج المستخدمين وسجلات التقدّم في قاعدة SQLite محلية (`quiz.db`) عبر
  `sqlite3` (المكتبة القياسية). الأسئلة في `questions.json` (مُولّد من `content.text`).
  لا تُضف ORM — استخدم `sqlite3` مباشرةً.
- **التوافق العكسي إلزامي:** عند قراءة السجلات من SQLite، السجلات القديمة بدون الحقل
  `status` تُعامَل كـ `completed` عبر `r.setdefault("status", "completed")`. الحقول
  الجديدة (`time_spent_seconds`، `tab_switches`، `wrong_question_ids`) اختيارية ولها
  قيم افتراضية. أي حقل جديد تضيفه يجب أن يمرّ بنفس نمط `setdefault` للحفاظ على السجلات القديمة.
- **نمط الكود:** تعليقات الدوال بالعربية داخل `"""..."""`، فواصل أسطر عربية في
  التعليقات المقطعية (مثل `# ─── المسار الرئيسي ───`). مسارات الملفات تُبنى من
  `BASE_DIR = os.path.dirname(os.path.abspath(__file__))` لا من مسارات مطلقة.
- **لا إطار عمل أمامي:** JavaScript عادي في `static/script.js`، الأنماط في
  `static/style.css`. لا تُضف React/Vue/أي framework.
- **لا CI/lint/format:** المشروع محلي بسيط — لا تُضف إعدادات lint أو format أو CI
  إلا بطلب صريح (YAGNI).

## بنية الملفات

```
qws/
├── AGENTS.md              # هذا الملف — إرشادات الوكلاء
├── app.py                 # خادم Flask: المسارات، منطق الاختبار، الحفظ/الاستئناف
├── content.text           # بنك الأسئلة الخام بالعربية (مصدر المحتوى)
├── parse_questions.py     # يحوّل content.text → questions.json (95 سؤال MCQ)
├── questions.json         # الأسئلة المُولّدة (مُدخلات التطبيق)
├── quiz.db                # قاعدة SQLite: نتائج المستخدمين وسجلات التقدّم
├── results.json           # نسخة احتياطية قديمة (تُرحّل إلى quiz.db تلقائيًا)
├── requirements.txt       # flask فقط
├── templates/             # قوالب Jinja2 (كلها dir="rtl" lang="ar")
│   ├── login.html         # تسجيل الدخول بالاسم + خيار استئناف
│   ├── quiz.html          # صفحة الاختبار مع المؤقت والحفظ التلقائي
│   ├── result.html        # نتيجة مستخدم واحد + مراجعة الإجابات الخاطئة
│   ├── results.html       # قائمة كل النتائج
│   ├── resume_error.html  # خطأ رمز استئناف غير صالح
│   └── stats.html         # لوحة الإحصائيات
├── static/
│   ├── script.js          # منطق الواجهة (المؤقت، الحفظ التلقائي، مكافحة الغش)
│   └── style.css          # الأنماط (RTL)
└── openspec/              # مواصفات مصدر الحقيقة + تغييرات قيد التقدم
    ├── config.yaml        # سياق المشروع وقواعد الكتابة
    ├── specs/             # 8 قدرات: anti-cheat, auth-simple, questions-data,
    │                      #   quiz-flow, quiz-timer, results-storage,
    │                      #   stats-dashboard, web-ui
    └── changes/           # تغييرات نشطة + archive/ للتغييرات المكتملة
```

## سير عمل OpenSpec (إلزامي)

- **مصدر الحقيقة:** `openspec/specs/` يوثّق السلوك الحالي للمشروع (8 قدرات). اقرأ
  المواصفة ذات الصلة قبل أي تعديل سلوكي.
- **اقترح قبل التعديل:** أي تغيير سلوكي غير تافه يبدأ باقتراح تغيير:
  ```powershell
  openspec new change <change-name> --goal "..."
  ```
  ثم اكتب `proposal.md` + `specs/<capability>/spec.md` (دلتا ADDED/MODIFIED/REMOVED)
  + `design.md` (للتغييرات غير التافهة) + `tasks.md`. لا تكتب كود التطبيق قبل
  التحقق من صحة الاقتراح.
- **التحقق قبل الاكتمال:** قبل الادعاء بأن عملك مكتمل، يجب أن يمر:
  ```powershell
  openspec validate <change-name>
  openspec validate --all
  openspec status --change <change-name>
  ```
- **الأرشفة بعد التنفيذ:** عند اكتمال كل المهام ونجاح التحقق:
  ```powershell
  openspec archive <change-name>
  ```
  يدمج الدلتا في `openspec/specs/` وينقل التغيير إلى `changes/archive/`.
- **قواعد الكتابة** (من `openspec/config.yaml`): الـ proposal والمواصفات والمهام
  بالعربية؛ استخدم `SHALL`/`MUST` في وصف المتطلبات؛ كل متطلب يحتاج سيناريو
  `#### Scenario:` بصيغة WHEN/THEN.

## القيود

- **محلي فقط:** `http://localhost:5000` — لا تنشر على خادم خارجي دون طلب صريح.
- **التخزين المحلي:** نتائج المستخدمين في SQLite (`quiz.db`)، الأسئلة في `questions.json`.
  لا تُضف قاعدة بيانات خارجية أو ORM.
- **مستخدم واحد لكل محاولة:** لا مصادقة متعددة المستخدمين؛ تسجيل دخول بسيط بالاسم
  بدون كلمة مرور.
- **لا تعديل سلوك موثّق دون اقتراح:** راجع قسم OpenSpec أعلاه.
