#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اختبارات أساسية لمنصة الاختبار التفاعلي QWS."""
import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("FLASK_APP", "app.py")

import app as app_module


@pytest.fixture
def client():
    """إنشاء عميل اختبار مع قاعدة بيانات مؤقتة."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    app_module.DB_FILE = db_path
    app_module.init_db()

    app_module.app.config["TESTING"] = True
    app_module.app.config["SECRET_KEY"] = "test-secret-key"

    with app_module.app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(db_path)


def test_login_page_loads(client):
    """صفحة تسجيل الدخول تُحمّل بنجاح."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert "اسم" in resp.data.decode("utf-8")


def test_quiz_requires_login(client):
    """الوصول لصفحة الاختبار بدون تسجيل دخول يُعيد التوجيه."""
    resp = client.get("/quiz")
    assert resp.status_code == 302
    assert "/quiz" not in resp.headers.get("Location", "")


def test_admin_login_page_loads(client):
    """صفحة دخول الإدارة تُحمّل بنجاح."""
    resp = client.get("/admin")
    assert resp.status_code == 200
    assert "كلمة المرور" in resp.data.decode("utf-8")


def test_admin_login_wrong_password(client):
    """كلمة مرور خاطئة تُعيد عرض صفحة الدخول مع رسالة خطأ."""
    resp = client.post("/admin", data={"password": "wrong"})
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "admin-login-form" in html
    assert "admin-alert-error" in html


def test_admin_login_correct_password(client):
    """كلمة مرور صحيحة تُوجّه إلى لوحة إدارة الأسئلة."""
    resp = client.post("/admin", data={"password": "admin123"}, follow_redirects=True)
    assert resp.status_code == 200
    assert "إدارة" in resp.data.decode("utf-8")


def test_admin_protected_without_session(client):
    """الوصول لصفحات الإدارة بدون جلسة يُعيد التوجيه للدخول."""
    resp = client.get("/admin/questions")
    assert resp.status_code == 302
    assert "/admin" in resp.headers.get("Location", "")

    resp = client.get("/admin/answers")
    assert resp.status_code == 302
    assert "/admin" in resp.headers.get("Location", "")


def test_stats_page_loads(client):
    """صفحة الإحصائيات تُحمّل بنجاح."""
    resp = client.get("/stats")
    assert resp.status_code == 200


def test_results_page_loads(client):
    """صفحة النتائج تُحمّل بنجاح."""
    resp = client.get("/results")
    assert resp.status_code == 200


def test_export_csv(client):
    """تصدير CSV يعمل ويُرجع النوع الصحيح."""
    resp = client.get("/export")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("Content-Type", "") or "attachment" in resp.headers.get("Content-Disposition", "")


def test_questions_json_valid():
    """ملف questions.json صالح ويحتوي على أسئلة."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    qpath = os.path.join(base, "questions.json")
    with open(qpath, encoding="utf-8") as f:
        questions = json.load(f)
    assert len(questions) > 0
    for q in questions:
        assert "id" in q
        assert "question" in q
        assert "options" in q
        assert "correct_answer" in q
        assert len(q["options"]) >= 2
