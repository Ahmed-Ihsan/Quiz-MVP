#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""نقطة دخول WSGI لنشر التطبيق على PythonAnywhere أو أي خادم WSGI."""
import os
import sys

# إضافة مجلد المشروع إلى مسار Python
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app import app as application  # noqa: E402

# تهيئة قاعدة البيانات عند أول تشغيل
from app import init_db  # noqa: E402
init_db()
