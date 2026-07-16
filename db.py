#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""طبقة تجريد قاعدة البيانات: Turso (libSQL) أو SQLite محلي.

إذا كانت متغيرات البيئة TURSO_URL و TURSO_AUTH_TOKEN موجودة،
يستخدم Turso (libSQL). وإلا يستخدم sqlite3 المحلي.
إذا فشل الاتصال بـ Turso، يتراجع تلقائيًا إلى sqlite3 المحلي.
"""
import os
import sys
import sqlite3

# متغيرات البيئة لـ Turso
TURSO_URL = os.environ.get("TURSO_URL", "")
TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN", "")

# تحديد نوع قاعدة البيانات
USE_TURSO = bool(TURSO_URL and TURSO_AUTH_TOKEN)
_DB_MODULE = sqlite3
_IS_LIBSQL = False

if USE_TURSO:
    try:
        import libsql_experimental as libsql
        _DB_MODULE = libsql
        _IS_LIBSQL = True
    except ImportError:
        try:
            import libsql
            _DB_MODULE = libsql
            _IS_LIBSQL = True
        except ImportError:
            USE_TURSO = False
            print("WARNING: TURSO_URL is set but libsql is not installed. "
                  "Falling back to local sqlite3. "
                  "Install with: pip install libsql-experimental", file=sys.stderr)


class OperationalError(Exception):
    """خطأ تشغيلي في قاعدة البيانات (متوافق مع sqlite3.OperationalError)."""
    pass


def _get_operational_error():
    """إرجاع فئة OperationalError المناسبة لنوع قاعدة البيانات."""
    if _IS_LIBSQL:
        return getattr(_DB_MODULE, "OperationalError", OperationalError)
    return sqlite3.OperationalError


def _turso_connect():
    """إنشاء اتصال بـ Turso (remote-only)."""
    return _DB_MODULE.connect(
        TURSO_URL,
        auth_token=TURSO_AUTH_TOKEN,
    )


def _test_turso_connection():
    """اختبار الاتصال بـ Turso. يُرجع True إذا نجح، False إذا فشل."""
    global USE_TURSO, _DB_MODULE, _IS_LIBSQL
    if not USE_TURSO:
        return False
    try:
        conn = _turso_connect()
        conn.execute("SELECT 1").fetchone()
        conn.close()
        return True
    except Exception as e:
        print(f"WARNING: Turso connection failed: {e}. "
              f"Falling back to local sqlite3.", file=sys.stderr)
        USE_TURSO = False
        _DB_MODULE = sqlite3
        _IS_LIBSQL = False
        return False


# اختبار الاتصال بـ Turso عند الاستيراد
if USE_TURSO:
    _test_turso_connection()


def connect(db_path):
    """إنشاء اتصال بقاعدة البيانات.

    مع Turso: يتصل بقاعدة libSQL البعيدة (remote-only).
    مع sqlite3: يتصل بملف محلي.
    """
    if USE_TURSO:
        try:
            conn = _turso_connect()
        except Exception:
            # تراجع طارئ إلى sqlite3 إذا فشل الاتصال وقت التشغيل
            conn = sqlite3.connect(db_path)
    else:
        conn = sqlite3.connect(db_path)

    # تعيين row_factory
    if hasattr(_DB_MODULE, "Row"):
        conn.row_factory = _DB_MODULE.Row
    elif hasattr(sqlite3, "Row"):
        conn.row_factory = sqlite3.Row

    return conn


def is_turso():
    """هل التطبيق يستخدم Turso؟"""
    return USE_TURSO


def sync(conn):
    """مزامنة الاتصال مع الخادم البعيد (Turso فقط)."""
    if USE_TURSO and hasattr(conn, "sync"):
        conn.sync()
