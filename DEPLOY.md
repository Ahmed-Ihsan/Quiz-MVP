# دليل النشر على PythonAnywhere

## الخطوات

### 1. إنشاء حساب
- اذهب إلى [pythonanywhere.com](https://www.pythonanywhere.com) وأنشئ حساب مجاني (Beginner account)

### 2. استنساخ المشروع من GitHub
1. اذهب إلى **Dashboard → Consoles → Bash**
2. نفّذ:
```bash
git clone https://github.com/Ahmed-Ihsan/Quiz-MVP.git ~/Quiz-MVP
```

### 3. إنشاء بيئة افتراضية وتثبيت المكتبات
في نفس الـ Bash console:
```bash
cd ~/Quiz-MVP
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. تهيئة قاعدة البيانات
```bash
python -c "from app import init_db; init_db()"
```

### 5. إنشاء تطبيق ويب (Web App)
1. اذهب إلى **Dashboard → Web → Add a new web app**
2. اختر **Manual configuration**
3. اختر **Python 3.10** (أو الأحدث المتاح)

### 6. إعداد WSGI
1. اذهب إلى **Web tab → Code section → WSGI configuration file**
2. اضغط على الرابط لتحرير الملف
3. **احذف كل المحتوى** والصق التالي:

```python
import os
import sys

project_home = "/home/YOUR_USERNAME/Quiz-MVP"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from wsgi import application as application  # noqa
```

> **استبدل** `YOUR_USERNAME` باسم المستخدم الخاص بك على PythonAnywhere

### 7. إعداد Virtualenv
1. في **Web tab → Virtualenv section**
2. اكتب المسار: `/home/YOUR_USERNAME/Quiz-MVP/venv`

### 8. إعداد الملفات الثابتة (Static Files)
في **Web tab → Static files section**، أضف:

| URL | Directory |
|-----|-----------|
| `/static` | `/home/YOUR_USERNAME/Quiz-MVP/static` |

### 9. إعادة التحميل
اضغط زر **Reload** في أعلى صفحة Web tab

### 10. فتح التطبيق
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
