## MODIFIED Requirements

### Requirement: حفظ النتائج في ملف JSON
النظام SHALL يحفظ نتيجة كل طالب في ملف `results.json`، مع تسجيل حالة السجل (`status`: `in_progress` أو `completed`)، وحقول التقدم (`answers`, `remaining_seconds`, `resume_code`, `started_at`) للسجلات غير المكتملة، وحقول التصحيح (`correct`, `total`, `percentage`, `date`, `time_spent_seconds`, `tab_switches`, `wrong_question_ids`) للسجلات المكتملة.

#### Scenario: حفظ سجل تقدم جديد
- **WHEN** يبدأ الطالب اختبارًا جديدًا
- **THEN** يُضاف سجل جديد إلى `results.json` بحقل `status: "in_progress"` و`resume_code` فريد و`answers` فارغة و`remaining_seconds` و`started_at`

#### Scenario: حفظ نتيجة طالب مكتملة
- **WHEN** ينهي المستخدم الاختبار ويتم حساب النتيجة
- **THEN** يُحدّث سجل التقدم الموجود (بـ `resume_code`) إلى `status: "completed"` مع حقول التصحيح، أو يُنشأ سجل `completed` جديد إن لم يوجد سجل تقدم

#### Scenario: إنشاء الملف عند عدم وجوده
- **WHEN** يتم حفظ نتيجة وملف `results.json` غير موجود
- **THEN** يتم إنشاء الملف بمصفوفة تحتوي على السجل الأول

#### Scenario: توافق عكسي مع السجلات القديمة
- **WHEN** يُحمّل النظام `results.json` ويحتوي على سجلات قديمة بدون حقل `status`
- **THEN** يعمل النظام بدون خطأ، وتُعامَل السجلات بدون `status` كـ `completed`، والحقول المفقودة كقيم افتراضية

### Requirement: عرض جميع النتائج
النظام SHALL يوفر مسار `/results` يعرض جدولًا بنتائج الطلاب المكتملة فقط (`status == "completed"`)، مرتبة من الأحدث للأقدم، ولا يعرض السجلات غير المكتملة.

#### Scenario: عرض جدول النتائج
- **WHEN** يفتح المستخدم صفحة `/results`
- **THEN** يظهر جدول يحتوي على السجلات المكتملة فقط: الاسم، عدد الإجابات الصحيحة، النسبة المئوية، والتاريخ

#### Scenario: لا توجد نتائج
- **WHEN** يفتح المستخدم `/results` ولا توجد نتائج مكتملة محفوظة
- **THEN** تظهر رسالة بالعربية "لا توجد نتائج بعد"

## ADDED Requirements

### Requirement: تصفية السجلات غير المكتملة في الإحصائيات والتصدير
النظام SHALL يصفي مسارات `/stats` و `/export` لتعالج السجلات المكتملة فقط (`status == "completed"`)، بحيث لا تؤثر السجلات غير المكتملة على المتوسطات أو نسب النجاح أو ملف CSV.

#### Scenario: إحصائيات بدون السجلات غير المكتملة
- **WHEN** يفتح المستخدم `/stats` وتوجد سجلات `in_progress` و `completed`
- **THEN** تُحسب الإحصائيات من السجلات `completed` فقط

#### Scenario: تصدير بدون السجلات غير المكتملة
- **WHEN** يفتح المستخدم `/export` وتوجد سجلات `in_progress` و `completed`
- **THEN** يحتوي ملف CSV على السجلات `completed` فقط
