# دليل النشر على PythonAnywhere

## الخطوات

### 1. إنشاء حساب
- اذهب إلى [pythonanywhere.com](https://www.pythonanywhere.com) وأنشئ حساب مجاني (Beginner account)

### 2. إعداد قاعدة بيانات Turso (اختياري - موصى به)

Turso قاعدة بيانات سحابية مبنية على SQLite (libSQL) تتيح الوصول للبيانات من أي مكان.

1. أنشئ حساب على [turso.tech](https://turso.tech)
2. من الـ Bash console في PythonAnywhere (أو جهازك)، ثبّت Turso CLI:
   ```bash
   curl -sSfL https://get.tur.so/install.sh | bash
   ```
3. سجّل الدخول وأنشئ قاعدة بيانات:
   ```bash
   turso auth login
   turso db create qws-quiz
   ```
4. احصل على رابط قاعدة البيانات ورمز المصادقة:
   ```bash
   turso db show qws-quiz --url
   turso db tokens create qws-quiz
   ```
5. سجّل القيم (ستحتاجها في الخطوة التالية):
   - `TURSO_URL`: رابط مثل `libsql://qws-quiz-xxxx.turso.io`
   - `TURSO_AUTH_TOKEN`: رمز المصادقة

> **بدون Turso:** التطبيق يستخدم SQLite محلي تلقائيًا إذا لم تُضبط هذه المتغيرات.

### 3. استنساخ المشروع من GitHub
1. اذهب إلى **Dashboard → Consoles → Bash**
2. نفّذ:
```bash
git clone https://github.com/Ahmed-Ihsan/Quiz-MVP.git ~/Quiz-MVP
```

### 4. إنشاء بيئة افتراضية وتثبيت المكتبات
في نفس الـ Bash console:
```bash
cd ~/Quiz-MVP
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-turso.txt
```

> **بدون Turso:** استخدم `pip install -r requirements.txt` بدلاً من ذلك.

### 5. تهيئة قاعدة البيانات
إذا كنت تستخدم Turso، اضبط متغيرات البيئة أولاً:
```bash
export TURSO_URL="libsql://qws-quiz-xxxx.turso.io"
export TURSO_AUTH_TOKEN="your-token-here"
python -c "from app import init_db; init_db()"
```

بدون Turso (SQLite محلي):
```bash
python -c "from app import init_db; init_db()"
```

### 6. إنشاء تطبيق ويب (Web App)
1. اذهب إلى **Dashboard → Web → Add a new web app**
2. اختر **Manual configuration**
3. اختر **Python 3.10** (أو الأحدث المتاح)

### 7. إعداد WSGI
1. اذهب إلى **Web tab → Code section → WSGI configuration file**
2. اضغط على الرابط لتحرير الملف
3. **احذف كل المحتوى** والصق التالي:

```python
import os
import sys

# متغيرات Turso (إن لزم — استبدل القيم بمعلوماتك)
os.environ["TURSO_URL"] = "libsql://qws-quiz-xxxx.turso.io"
os.environ["TURSO_AUTH_TOKEN"] = "your-token-here"

project_home = "/home/YOUR_USERNAME/Quiz-MVP"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from wsgi import application as application  # noqa
```

> **استبدل** `YOUR_USERNAME` باسم المستخدم الخاص بك على PythonAnywhere
> **بدون Turso:** احذف سطري `os.environ` إذا كنت تستخدم SQLite محلي

### 8. إعداد Virtualenv
1. في **Web tab → Virtualenv section**
2. اكتب المسار: `/home/YOUR_USERNAME/Quiz-MVP/venv`

### 9. إعداد الملفات الثابتة (Static Files)
في **Web tab → Static files section**، أضف:

| URL | Directory |
|-----|-----------|
| `/static` | `/home/YOUR_USERNAME/Quiz-MVP/static` |

### 10. إعادة التحميل
اضغط زر **Reload** في أعلى صفحة Web tab

### 11. فتح التطبيق
رابط التطبيق سيكون:
```
https://YOUR_USERNAME.pythonanywhere.com
```

شارك هذا الرابط مع أصدقائك!

---

## ملاحظات مهمة

- **الحساب المجاني (Beginner):** يدعم تطبيق واحد، 512MB تخزين، وعدد محدود من الزيارات اليومية
- **قاعدة البيانات:** `quiz.db` تُنشأ تلقائيًا عند أول تشغيل
- **كلمة مرور الإدارة:** `admin123` — غيّرها من `app.py` قبل النشر للإنتاج
- **التحديث من GitHub:** لإعادة تحديث التطبيق بعد تعديلات:
  ```bash
  cd ~/Quiz-MVP
  git pull origin master
  ```
  ثم اضغط **Reload** في صفحة Web tab

---

## استكشاف الأخطاء

### خطأ 500 (Internal Server Error)
- تحقق من **Web tab → Error log**
- تأكد أن `YOUR_USERNAME` صحيح في ملف WSGI
- تأكد أن `venv` مُفعّل و`flask` مُثبّت

### الصور/الأنماط لا تظهر
- تأكد من إعداد **Static files** بشكل صحيح (الخطوة 8)

### قاعدة البيانات لا تعمل
- تأكد من تنفيذ الخطوة 4 (تهيئة قاعدة البيانات)
- تحقق من صلاحيات الكتابة في مجلد المشروع
