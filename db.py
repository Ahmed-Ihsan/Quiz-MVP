#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""طبقة تجريد قاعدة البيانات: Turso (libSQL) أو SQLite محلي.

إذا كانت متغيرات البيئة TURSO_URL و TURSO_AUTH_TOKEN موجودة،
يستخدم Turso (libSQL). وإلا يستخدم sqlite3 المحلي.
"""
import os

# متغيرات البيئة لـ Turso
TURSO_URL = os.environ.get("TURSO_URL", "")
TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN", "")

# تحديد نوع قاعدة البيانات
USE_TURSO = bool(TURSO_URL and TURSO_AUTH_TOKEN)

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
            # تراجع إلى sqlite3 إذا لم تكن libsql مُثبّتة
            import sqlite3
            _DB_MODULE = sqlite3
            _IS_LIBSQL = False
            USE_TURSO = False
else:
    import sqlite3
    _DB_MODULE = sqlite3
    _IS_LIBSQL = False


class OperationalError(Exception):
    """خطأ تشغيلي في قاعدة البيانات (متوافق مع sqlite3.OperationalError)."""
    pass


def _get_operational_error():
    """إرجاع فئة OperationalError المناسبة لنوع قاعدة البيانات."""
    if _IS_LIBSQL:
        return getattr(_DB_MODULE, "OperationalError", OperationalError)
    return sqlite3.OperationalError


def connect(db_path):
    """إنشاء اتصال بقاعدة البيانات.

    مع Turso: يتصل بقاعدة libSQL البعيدة (مع نسخة محلية embedded replica).
    مع sqlite3: يتصل بملف محلي.
    """
    if USE_TURSO:
        conn = _DB_MODULE.connect(
            TURSO_URL,
            auth_token=TURSO_AUTH_TOKEN,
            sync_url=TURSO_URL,
        )
        # مزامنة النسخة المحلية مع البعيدة
        if hasattr(conn, "sync"):
            conn.sync()
    else:
        conn = _DB_MODULE.connect(db_path)

    # تعيين row_factory إذا كان مدعومًا
    if hasattr(_DB_MODULE, "Row"):
        conn.row_factory = _DB_MODULE.Row

    return conn


def is_turso():
    """هل التطبيق يستخدم Turso؟"""
    return USE_TURSO


def sync(conn):
    """مزامنة الاتصال مع الخادم البعيد (Turso فقط)."""
    if USE_TURSO and hasattr(conn, "sync"):
        conn.sync()
