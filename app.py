#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""منصة اختبار تفاعلي عن الأردوينو وبايثون وإنترنت الأشياء."""
import csv
import io
import json
import os
import random
import secrets
import statistics
import sqlite3
import time
from datetime import datetime

from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    redirect,
    url_for,
    session,
)

# أبجدية غير ملتبسة لرمز الاستئناف: A-Z بدون O/I، 2-9 بدون 0/1
RESUME_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
RESUME_CODE_LENGTH = 6

app = Flask(__name__)
app.secret_key = "qws-quiz-secret-key-2026"

# تخزين مؤقت لنتائج لم تُعرَض بعد (يمنع تجاوز حجم كوكي الجلسة)
_pending_results = {}

# مدة المؤقت بالدقائق — اضبط على 0 لتعطيل المؤقت والإرسال التلقائي
QUIZ_TIMER_MINUTES = 30

# كلمة مرور لوحة الإدارة
ADMIN_PASSWORD = "admin123"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_FILE = os.path.join(BASE_DIR, "questions.json")
RESULTS_FILE = os.path.join(BASE_DIR, "results.json")
DB_FILE = os.path.join(BASE_DIR, "quiz.db")


def load_questions():
    """تحميل الأسئلة من ملف JSON."""
    # utf-8-sig يتجاهل BOM إن وُجد
    with open(QUESTIONS_FILE, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def save_questions(questions):
    """حفظ الأسئلة في ملف JSON (كتابة كاملة بترميز UTF-8)."""
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)


def init_db():
    """تهيئة قاعدة بيانات SQLite وإنشاء الجدول إن لم يوجد.

    تُرحّل سجلات `results.json` الحالية إلى SQLite لمرة واحدة عند أول تشغيل
    (إذا كان الجدول فارغًا والملف موجودًا وصالحًا). لا تُحذف `results.json`.
    """
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS results (
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
            )"""
        )

        # جدول منفصل لتفاصيل إجابات الطلاب — يظهر للأدمن فقط
        conn.execute(
            """CREATE TABLE IF NOT EXISTS answer_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                question_id INTEGER,
                section TEXT,
                question_text TEXT,
                code TEXT,
                user_answer TEXT,
                correct_answer TEXT,
                correct_text TEXT,
                is_correct INTEGER DEFAULT 0,
                date TEXT
            )"""
        )
        # إضافة عمود image لجدول answer_details إن لم يوجد
        try:
            conn.execute("ALTER TABLE answer_details ADD COLUMN image TEXT")
        except sqlite3.OperationalError:
            pass  # العمود موجود بالفعل

        conn.commit()
        count = conn.execute("SELECT COUNT(*) FROM results").fetchone()[0]
        if count == 0 and os.path.exists(RESULTS_FILE):
            _migrate_from_json(conn)
    finally:
        conn.close()


def _migrate_from_json(conn):
    """استيراد سجلات results.json إلى SQLite (تُستدعى مرة واحدة من init_db).

    تتسامح مع الملفات التالفة: إذا فشل json.load تُتجاوز الترحيل بهدوء.
    """
    try:
        with open(RESULTS_FILE, "r", encoding="utf-8-sig") as f:
            records = json.load(f)
    except (ValueError, OSError):
        return
    for r in records:
        _insert_record(conn, r)
    conn.commit()


def _insert_record(conn, r):
    """إدراج سجل واحد في جدول results من قاموس (للاستخدام الداخلي)."""
    r.setdefault("status", "completed")
    r.setdefault("time_spent_seconds", 0)
    r.setdefault("tab_switches", 0)
    r.setdefault("wrong_question_ids", [])
    answers = r.get("answers")
    if isinstance(answers, dict):
        answers = json.dumps(answers, ensure_ascii=False)
    wrong = r.get("wrong_question_ids")
    if isinstance(wrong, list):
        wrong = json.dumps(wrong, ensure_ascii=False)
    conn.execute(
        """INSERT INTO results
           (name, status, resume_code, answers, remaining_seconds, started_at,
            correct, total, percentage, date, time_spent_seconds, tab_switches,
            wrong_question_ids)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            r.get("name", ""),
            r.get("status", "completed"),
            r.get("resume_code"),
            answers,
            r.get("remaining_seconds"),
            r.get("started_at"),
            r.get("correct"),
            r.get("total"),
            r.get("percentage"),
            r.get("date"),
            r.get("time_spent_seconds", 0),
            r.get("tab_switches", 0),
            wrong,
        ),
    )


def _row_to_dict(row):
    """تحويل صف SQLite إلى قاموس مع توافق عكسي وتفكيك حقول JSON."""
    d = dict(row)
    d.pop("id", None)
    # توافق عكسي: الحقول الاختيارية وقيمها الافتراضية
    d.setdefault("status", "completed")
    d.setdefault("time_spent_seconds", 0)
    d.setdefault("tab_switches", 0)
    d.setdefault("wrong_question_ids", [])
    # تفكيك حقول JSON المخزّنة كنص
    answers = d.get("answers")
    if isinstance(answers, str):
        d["answers"] = json.loads(answers) if answers else {}
    elif answers is None:
        d["answers"] = {}
    wrong = d.get("wrong_question_ids")
    if isinstance(wrong, str):
        d["wrong_question_ids"] = json.loads(wrong) if wrong else []
    elif wrong is None:
        d["wrong_question_ids"] = []
    return d


def load_results():
    """تحميل جميع النتائج من قاعدة SQLite (قائمة قواميس).

    ضمان توافق عكسي مع السجلات القديمة: الحقول الجديدة (time_spent_seconds،
    tab_switches، wrong_question_ids) اختيارية وتُعامَل كقيم افتراضية عند فقدها.
    السجلات بدون `status` تُعامَل كـ `completed` (توافق عكسي).
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("SELECT * FROM results").fetchall()
        return [_row_to_dict(row) for row in rows]
    finally:
        conn.close()


def save_results(results):
    """حفظ النتائج في قاعدة SQLite (استبدال كامل ذري ضمن معاملة واحدة).

    تُحذف كل السجلات وتُعاد إدراجها ضمن معاملة واحدة لضمان الكتابة الذرية.
    """
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("DELETE FROM results")
        for r in results:
            _insert_record(conn, r)
        conn.commit()
    finally:
        conn.close()


def save_answer_details(name, questions, answers_map, date_str):
    """حفظ تفاصيل إجابات الطالب (لكل سؤال) في جدول answer_details.

    يُستدعى مرة واحدة عند إرسال الاختبار. البيانات هنا للأدمن فقط ولا تُعرَض للطالب.
    """
    conn = sqlite3.connect(DB_FILE)
    try:
        for q in questions:
            qid = str(q["id"])
            user_ans = answers_map.get(qid, "")
            correct = q["correct_answer"]
            is_correct = 1 if user_ans == correct else 0
            conn.execute(
                """INSERT INTO answer_details
                   (student_name, question_id, section, question_text, code,
                    user_answer, correct_answer, correct_text, is_correct, date, image)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    name,
                    q["id"],
                    q.get("section", ""),
                    q["question"],
                    q.get("code"),
                    q.get("image"),
                    user_ans if user_ans else "لم يتم الإجابة",
                    correct,
                    q["options"].get(correct, ""),
                    is_correct,
                    date_str,
                ),
            )
        conn.commit()
    finally:
        conn.close()


def load_answer_details(name, date_str):
    """تحميل تفاصيل إجابات طالب محدد (بالاسم والتاريخ) من جدول answer_details."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """SELECT * FROM answer_details
               WHERE student_name = ? AND date = ?
               ORDER BY question_id""",
            (name, date_str),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def generate_resume_code():
    """توليد رمز استئناف فريد من 6 أحرف من أبجدية غير ملتبسة باستخدام secrets.

    يتحقق من التفرّد مقابل السجلات الحالية في SQLite ويعيد التوليد إن لزم.
    """
    conn = sqlite3.connect(DB_FILE)
    try:
        rows = conn.execute("SELECT resume_code FROM results WHERE resume_code IS NOT NULL").fetchall()
        existing_codes = {row[0] for row in rows}
    finally:
        conn.close()
    while True:
        code = "".join(secrets.choice(RESUME_ALPHABET) for _ in range(RESUME_CODE_LENGTH))
        if code not in existing_codes:
            return code


def find_in_progress(name):
    """إرجاع أحدث سجل `in_progress` لاسم معين، أو None إن لم يوجد."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            """SELECT * FROM results
               WHERE status = 'in_progress' AND name = ?
               ORDER BY started_at DESC LIMIT 1""",
            (name,),
        ).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        conn.close()


def find_by_resume_code(code):
    """إرجاع سجل التقدم بـ `resume_code` المطابق، أو None إن لم يوجد."""
    if not code:
        return None
    code = code.strip().upper()
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT * FROM results WHERE UPPER(resume_code) = ?", (code,)
        ).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        conn.close()


def upsert_progress(record):
    """تحديث سجل تقدم موجود (بـ resume_code) أو إضافته إن لم يوجد.

    يُرجع السجل النهائي.
    """
    code = record.get("resume_code")
    conn = sqlite3.connect(DB_FILE)
    try:
        if code:
            existing = conn.execute(
                "SELECT 1 FROM results WHERE resume_code = ?", (code,)
            ).fetchone()
            if existing:
                # تحديث: حذف السجل القديم وإدراج الجديد ضمن نفس المعاملة
                conn.execute("DELETE FROM results WHERE resume_code = ?", (code,))
        _insert_record(conn, record)
        conn.commit()
    finally:
        conn.close()
    return record


# ─── تهيئة قاعدة البيانات عند استيراد الوحدة ───
init_db()


# ─── المسار الرئيسي: تسجيل الدخول ───
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            return render_template("login.html", error="الرجاء إدخال اسمك")

        # البحث عن اختبار غير مكتمل بنفس الاسم
        in_progress = find_in_progress(name)
        action = request.form.get("resume_action", "")

        # إن وُجد سجل غير مكتمل ولم يختر المستخدم بعد: اعرض خيار المتابعة/بدء جديد
        if in_progress and action not in ("resume", "new"):
            return render_template(
                "login.html",
                resume_name=name,
                resume_code=in_progress.get("resume_code", ""),
            )

        if in_progress and action == "resume":
            # متابعة الاختبار غير المكتمل عبر رمز الاستئناف
            session["name"] = name
            session["submitted"] = False
            session["resume_code"] = in_progress.get("resume_code")
            return redirect(url_for("resume", code=in_progress.get("resume_code", "")))

        # بدء جديد: حذف أي سجلات in_progress قديمة بنفس الاسم (تُهمَل/تُحذف)
        if in_progress:
            results = load_results()
            results = [
                r for r in results
                if not (r.get("status") == "in_progress" and r.get("name") == name)
            ]
            save_results(results)

        session["name"] = name
        session["submitted"] = False
        session.pop("resume_code", None)
        return redirect(url_for("quiz"))
    return render_template("login.html")


# ─── صفحة الاختبار ───
@app.route("/quiz")
def quiz():
    if "name" not in session:
        return redirect(url_for("login"))

    questions = load_questions()
    # خلط ترتيب خيارات كل سؤال عشوائيًا عند كل تحميل للصفحة
    for q in questions:
        items = list(q["options"].items())
        random.shuffle(items)
        q["options"] = dict(items)
    total_seconds = QUIZ_TIMER_MINUTES * 60 if QUIZ_TIMER_MINUTES and QUIZ_TIMER_MINUTES > 0 else None

    # تحديد سجل التقدم: استئناف سجل موجود أو إنشاء سجل in_progress جديد
    resume_code = session.get("resume_code")
    record = find_by_resume_code(resume_code) if resume_code else None

    if not (record and record.get("status") == "in_progress"):
        # اختبار جديد: إنشاء سجل in_progress مع رمز استئناف فريد
        resume_code = generate_resume_code()
        record = {
            "name": session["name"],
            "status": "in_progress",
            "resume_code": resume_code,
            "answers": {},
            "remaining_seconds": total_seconds,
            "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        upsert_progress(record)
        session["resume_code"] = resume_code

    # قراءة الحقول المحفوظة للاستئناف
    saved_answers = record.get("answers", {}) or {}
    remaining_seconds = record.get("remaining_seconds")
    # توافق: إن كان remaining_seconds مفقودًا والمؤقت مفعّلًا، ابدأ من الكامل
    if remaining_seconds is None and total_seconds is not None:
        remaining_seconds = total_seconds

    return render_template(
        "quiz.html",
        questions=questions,
        timer_minutes=QUIZ_TIMER_MINUTES,
        resume_code=resume_code,
        saved_answers=saved_answers,
        remaining_seconds=remaining_seconds,
    )


# ─── الحفظ التلقائي للإجابات (/save) ───
@app.route("/save", methods=["POST"])
def save():
    if "name" not in session:
        return jsonify({"ok": False, "error": "no_session"}), 403

    # رفض الحفظ التلقائي بعد إرسال الاختبار (يمنع سباق beforeunload مع /submit)
    if session.get("submitted", False):
        return jsonify({"ok": False, "error": "already_submitted"}), 403

    # قبول JSON (sendBeacon) أو بيانات نموذج
    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict()

    resume_code = (data.get("resume_code") or "").strip().upper()
    answers = data.get("answers", {})
    # answers قد تأتي سلسلة JSON من نموذج
    if isinstance(answers, str):
        try:
            answers = json.loads(answers) if answers else {}
        except (ValueError, TypeError):
            answers = {}

    try:
        remaining_seconds = data.get("remaining_seconds")
        if remaining_seconds in (None, "", "null"):
            remaining_seconds = None
        else:
            remaining_seconds = int(remaining_seconds)
    except (TypeError, ValueError):
        remaining_seconds = None

    record = find_by_resume_code(resume_code)
    if record and record.get("status") == "in_progress":
        record["answers"] = answers
        if remaining_seconds is not None:
            record["remaining_seconds"] = remaining_seconds
        upsert_progress(record)
        return jsonify({"ok": True})

    # منع الكتابة فوق سجل مكتمل (يمنع سباق beforeunload مع /submit)
    if record and record.get("status") == "completed":
        return jsonify({"ok": False, "error": "already_completed"}), 403

    # حالة نادرة: لا يوجد سجل تقدم — أنشئ سجل in_progress جديد
    if not resume_code:
        resume_code = generate_resume_code()
    new_record = {
        "name": session["name"],
        "status": "in_progress",
        "resume_code": resume_code,
        "answers": answers,
        "remaining_seconds": remaining_seconds,
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    upsert_progress(new_record)
    session["resume_code"] = resume_code
    return jsonify({"ok": True})


# ─── استئناف الاختبار عبر الرمز (/resume/<code>) ───
@app.route("/resume/<code>")
def resume(code):
    record = find_by_resume_code(code)
    if record and record.get("status") == "in_progress":
        session["name"] = record.get("name")
        session["submitted"] = False
        session["resume_code"] = record.get("resume_code")
        return redirect(url_for("quiz"))
    # الرمز غير صحيح أو منتهي
    return render_template("resume_error.html"), 404


# ─── استقبال الإجابات والتصحيح ───
@app.route("/submit", methods=["POST"])
def submit():
    if "name" not in session:
        return redirect(url_for("login"))

    questions = load_questions()
    total = len(questions)
    correct_count = 0
    wrong_question_ids = []

    user_answers_map = {}
    for q in questions:
        qid = str(q["id"])
        user_answer = request.form.get(f"q{qid}", "").strip()
        user_answers_map[qid] = user_answer
        correct = q["correct_answer"]

        if user_answer == correct:
            correct_count += 1
        else:
            wrong_question_ids.append(q["id"])

    percentage = round((correct_count / total) * 100, 2) if total > 0 else 0

    # حساب الوقت المستغرق من الوقت المتبقي المرسل من العميل (النهج C)
    try:
        remaining_seconds = request.form.get("remaining_seconds", "")
        remaining_seconds = int(remaining_seconds) if remaining_seconds not in ("", None) else None
    except (TypeError, ValueError):
        remaining_seconds = None

    if QUIZ_TIMER_MINUTES and QUIZ_TIMER_MINUTES > 0 and remaining_seconds is not None:
        time_spent_seconds = max(0, QUIZ_TIMER_MINUTES * 60 - remaining_seconds)
    else:
        time_spent_seconds = 0

    # قراءة عدد مرات تبديل التبويب من النموذج (حقل مخفي يُحدّث من JavaScript)
    try:
        tab_switches = int(request.form.get("tab_switches", "0"))
    except (TypeError, ValueError):
        tab_switches = 0

    # رمز الاستئناف من النموذج لربط السجل النهائي بسجل التقدم
    resume_code = (request.form.get("resume_code") or "").strip().upper()

    # منع تكرار الحفظ في نفس الجلسة
    if not session.get("submitted", False):
        results = load_results()
        completed_fields = {
            "name": session["name"],
            "correct": correct_count,
            "total": total,
            "percentage": percentage,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "time_spent_seconds": time_spent_seconds,
            "tab_switches": tab_switches,
            "wrong_question_ids": wrong_question_ids,
            "status": "completed",
        }

        # تحديث سجل التقدم الموجود إلى completed بدلًا من إضافة سجل جديد
        updated = False
        if resume_code:
            for i, r in enumerate(results):
                if (r.get("resume_code") or "").upper() == resume_code:
                    completed_fields["resume_code"] = r.get("resume_code")
                    results[i] = completed_fields
                    updated = True
                    break

        if not updated:
            # توافق عكسي: لا يوجد سجل تقدم — أنشئ سجل completed جديد
            if resume_code:
                completed_fields["resume_code"] = resume_code
            results.append(completed_fields)

        save_results(results)
        # حفظ تفاصيل الإجابات في جدول منفصل للأدمن فقط
        save_answer_details(
            session["name"], questions, user_answers_map,
            completed_fields["date"],
        )
        session["submitted"] = True

    # تخزين النتيجة على الخادم بدل الجلسة (يمنع تجاوز حجم كوكي الجلسة)
    # لا تُمرَّر الإجابات الصحيحة/الخاطئة للطالب — تُحفظ في answer_details للأدمن
    result_token = secrets.token_hex(16)
    _pending_results[result_token] = {
        "correct": correct_count,
        "total": total,
        "percentage": percentage,
    }
    session["result_token"] = result_token

    return redirect(url_for("result", submitted=1))


# ─── صفحة النتيجة ───
@app.route("/result")
def result():
    if "name" not in session:
        return redirect(url_for("login"))

    result_token = session.get("result_token")
    if not result_token or result_token not in _pending_results:
        return redirect(url_for("quiz"))

    # استرجاع النتيجة من التخزين المؤقت وحذفها (استخدام مرة واحدة)
    result_data = _pending_results.pop(result_token)
    percentage = result_data["percentage"]

    # رسالة التقييم
    if percentage >= 90:
        grade = "ممتاز"
    elif percentage >= 70:
        grade = "جيد"
    else:
        grade = "يحتاج تحسين"

    return render_template(
        "result.html",
        name=session["name"],
        correct=result_data["correct"],
        total=result_data["total"],
        percentage=percentage,
        grade=grade,
    )


# ─── صفحة جميع النتائج ───
@app.route("/results")
def results():
    all_results = load_results()
    # تصفية السجلات المكتملة فقط
    all_results = [r for r in all_results if r.get("status") == "completed"]
    # ترتيب من الأحدث للأقدم
    all_results = sorted(all_results, key=lambda r: r.get("date", ""), reverse=True)
    return render_template("results.html", results=all_results)


# ─── تصدير النتائج إلى CSV ───
@app.route("/export")
def export():
    all_results = load_results()
    # تصفية السجلات المكتملة فقط
    all_results = [r for r in all_results if r.get("status") == "completed"]
    output = io.StringIO()
    # كتابة BOM لضمان ظهور العربية بشكل صحيح في Excel
    output.write("\ufeff")
    writer = csv.writer(output)
    writer.writerow([
        "الاسم",
        "الإجابات الصحيحة",
        "الإجمالي",
        "النسبة المئوية",
        "التاريخ",
        "الوقت المستغرق (ث)",
        "تبديلات التبويب",
    ])
    for r in all_results:
        writer.writerow([
            r.get("name", ""),
            r.get("correct", 0),
            r.get("total", 0),
            r.get("percentage", 0),
            r.get("date", ""),
            r.get("time_spent_seconds", 0),
            r.get("tab_switches", 0),
        ])
    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": 'attachment; filename="results.csv"'},
    )


def _fmt_time(sec):
    """تنسيق الوقت بالعربية (ساعات/دقائق/ثواني)."""
    if sec <= 0:
        return "—"
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}س {m}د {s}ث"
    if m > 0:
        return f"{m}د {s}ث"
    return f"{s}ث"


# ─── لوحة الإحصائيات ───
@app.route("/stats")
def stats():
    all_results = load_results()
    # تصفية السجلات المكتملة فقط قبل حساب الإحصائيات
    all_results = [r for r in all_results if r.get("status") == "completed"]
    if not all_results:
        return render_template("stats.html", has_results=False)

    total_students = len(all_results)
    percentages = [r.get("percentage", 0) for r in all_results]
    avg_percentage = round(sum(percentages) / total_students, 2)
    highest = max(percentages)
    lowest = min(percentages)
    passed = sum(1 for p in percentages if p >= 50)
    pass_rate = round((passed / total_students) * 100, 2)

    # ─── إحصائيات متقدمة ───
    median_percentage = round(statistics.median(percentages), 2)
    stdev_percentage = round(statistics.stdev(percentages), 2) if len(percentages) > 1 else 0
    score_range = round(highest - lowest, 2)
    if len(percentages) >= 4:
        q1_percentage = round(statistics.quantiles(percentages, n=4)[0], 2)
        q3_percentage = round(statistics.quantiles(percentages, n=4)[2], 2)
    else:
        q1_percentage = lowest
        q3_percentage = highest

    # ─── أصعب الأسئلة ───
    questions = load_questions()
    qid_to_text = {q["id"]: q["question"] for q in questions}
    wrong_counts = {}
    for r in all_results:
        for qid in r.get("wrong_question_ids", []):
            wrong_counts[qid] = wrong_counts.get(qid, 0) + 1

    hardest = []
    for qid, count in wrong_counts.items():
        error_rate = round((count / total_students) * 100, 2)
        hardest.append({
            "id": qid,
            "text": qid_to_text.get(qid, f"سؤال {qid}"),
            "error_count": count,
            "error_rate": error_rate,
        })
    hardest.sort(key=lambda x: x["error_rate"], reverse=True)
    hardest = hardest[:5]

    # ─── توزيع الدرجات ───
    distribution = {
        "ممتاز (≥90%)": sum(1 for p in percentages if p >= 90),
        "جيد (70-89%)": sum(1 for p in percentages if 70 <= p < 90),
        "متوسط (50-69%)": sum(1 for p in percentages if 50 <= p < 70),
        "ضعيف (<50%)": sum(1 for p in percentages if p < 50),
    }
    max_dist = max(distribution.values()) if distribution else 1

    # ─── شرائح الرسم الدائري ───
    pie_colors = ["var(--success)", "var(--primary)", "var(--warning)", "var(--danger)"]
    pie_segments = []
    cumulative_pct = 0
    for i, (label, count) in enumerate(distribution.items()):
        pct = round((count / total_students) * 100, 1) if total_students else 0
        pie_segments.append({
            "label": label,
            "count": count,
            "pct": pct,
            "start_pct": cumulative_pct,
            "end_pct": cumulative_pct + pct,
            "color": pie_colors[i],
        })
        cumulative_pct += pct

    # ─── تحليل الأقسام ───
    section_questions = {}
    for q in questions:
        sec = q["section"]
        if sec not in section_questions:
            section_questions[sec] = []
        section_questions[sec].append(q["id"])

    section_wrong = {sec: 0 for sec in section_questions}
    for r in all_results:
        wrong_ids = set(r.get("wrong_question_ids", []))
        for sec, qids in section_questions.items():
            section_wrong[sec] += len(wrong_ids & set(qids))

    section_analysis = []
    for sec, qids in section_questions.items():
        total_possible = len(qids) * total_students
        wrong = section_wrong[sec]
        correct = total_possible - wrong
        rate = round((correct / total_possible) * 100, 2) if total_possible else 0
        section_analysis.append({
            "section": sec,
            "total_qs": len(qids),
            "correct_rate": rate,
            "wrong_count": wrong,
            "correct_count": correct,
        })
    section_analysis.sort(key=lambda x: x["correct_rate"], reverse=True)

    # ─── تحليل الوقت والغش ───
    times = [r.get("time_spent_seconds", 0) for r in all_results if r.get("time_spent_seconds", 0) > 0]
    avg_time = round(sum(times) / len(times)) if times else 0
    max_time = max(times) if times else 0
    min_time = min(times) if times else 0

    tab_switches_list = [r.get("tab_switches", 0) for r in all_results]
    avg_tab_switches = round(sum(tab_switches_list) / total_students, 1)
    max_tab_switches = max(tab_switches_list) if tab_switches_list else 0
    suspicious_count = sum(1 for t in tab_switches_list if t >= 3)

    # ─── الاتجاه الزمني ───
    date_scores = {}
    for r in all_results:
        date_str = r.get("date", "")[:10]
        if date_str:
            if date_str not in date_scores:
                date_scores[date_str] = []
            date_scores[date_str].append(r.get("percentage", 0))

    trend_data = []
    for date_str in sorted(date_scores.keys()):
        scores = date_scores[date_str]
        trend_data.append({
            "date": date_str,
            "avg": round(sum(scores) / len(scores), 2),
            "count": len(scores),
        })

    # ─── جدول أداء جميع الأسئلة ───
    all_questions_analysis = []
    for q in questions:
        qid = q["id"]
        wrong_count = wrong_counts.get(qid, 0)
        error_rate = round((wrong_count / total_students) * 100, 2) if total_students else 0
        text = q["question"]
        if len(text) > 60:
            text = text[:60] + "..."
        all_questions_analysis.append({
            "id": qid,
            "section": q["section"],
            "text": text,
            "error_count": wrong_count,
            "error_rate": error_rate,
            "correct_rate": round(100 - error_rate, 2),
        })
    all_questions_analysis.sort(key=lambda x: x["error_rate"], reverse=True)

    return render_template(
        "stats.html",
        has_results=True,
        total_students=total_students,
        avg_percentage=avg_percentage,
        highest=highest,
        lowest=lowest,
        pass_rate=pass_rate,
        hardest=hardest,
        distribution=distribution,
        max_dist=max_dist if max_dist > 0 else 1,
        # إحصائيات متقدمة
        median_percentage=median_percentage,
        stdev_percentage=stdev_percentage,
        score_range=score_range,
        q1_percentage=q1_percentage,
        q3_percentage=q3_percentage,
        # تحليل الأقسام
        section_analysis=section_analysis,
        # تحليل الوقت والغش
        avg_time_fmt=_fmt_time(avg_time),
        max_time_fmt=_fmt_time(max_time),
        min_time_fmt=_fmt_time(min_time),
        avg_tab_switches=avg_tab_switches,
        max_tab_switches=max_tab_switches,
        suspicious_count=suspicious_count,
        # الاتجاه الزمني
        trend_data=json.dumps(trend_data, ensure_ascii=False),
        trend_count=len(trend_data),
        # جدول الأسئلة الكامل
        all_questions_analysis=all_questions_analysis,
        # شرائح الرسم الدائري
        pie_segments=pie_segments,
    )


# ─── لوحة إدارة الأسئلة ───
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    """تسجيل دخول الإدارة بكلمة مرور بسيطة."""
    next_url = request.args.get("next") or request.form.get("next")

    if session.get("is_admin"):
        return redirect(next_url or url_for("admin_questions"))

    if request.method == "POST":
        password = request.form.get("password", "").strip()
        if password == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(next_url or url_for("admin_questions"))
        return render_template("admin.html", admin_login=True, login_error="كلمة المرور غير صحيحة", next_url=next_url)

    return render_template("admin.html", admin_login=True, next_url=next_url)


@app.route("/admin/questions")
def admin_questions():
    """عرض قائمة جميع الأسئلة مع أزرار التعديل والحذف."""
    if not session.get("is_admin"):
        return redirect(url_for("admin_login", next=request.path))

    questions = load_questions()
    # تجميع الأقسام الفريدة للاقتراح في حقل القسم
    sections = sorted(set(q["section"] for q in questions))
    return render_template("admin.html", questions=questions, sections=sections)


@app.route("/admin/questions/add", methods=["POST"])
def admin_add_question():
    """إضافة سؤال جديد إلى questions.json."""
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    questions = load_questions()
    new_id = max(q["id"] for q in questions) + 1 if questions else 1

    question = _build_question_from_form(request, new_id)
    if question is None:
        return render_template("admin.html", questions=load_questions(),
                               sections=sorted(set(q["section"] for q in load_questions())),
                               form_error="الرجاء تعبئة نص السؤال والخيارات الأربعة")

    questions.append(question)
    save_questions(questions)

    sections = sorted(set(q["section"] for q in questions))
    return render_template("admin.html", questions=questions, sections=sections,
                           form_success="تمت إضافة السؤال بنجاح")


@app.route("/admin/questions/<int:qid>/edit", methods=["GET", "POST"])
def admin_edit_question(qid):
    """تعديل سؤال موجود."""
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    questions = load_questions()
    target = None
    for q in questions:
        if q["id"] == qid:
            target = q
            break

    if target is None:
        return redirect(url_for("admin_questions"))

    if request.method == "POST":
        updated = _build_question_from_form(request, qid)
        if updated is None:
            sections = sorted(set(q["section"] for q in questions))
            return render_template("admin.html", questions=questions, sections=sections,
                                   form_error="الرجاء تعبئة نص السؤال والخيارات الأربعة",
                                   edit_question=target)

        # استبدال السؤال في مكانه
        for i, q in enumerate(questions):
            if q["id"] == qid:
                questions[i] = updated
                break
        save_questions(questions)
        sections = sorted(set(q["section"] for q in questions))
        return render_template("admin.html", questions=questions, sections=sections,
                               form_success="تم تعديل السؤال بنجاح")

    # GET: عرض نموذج التعديل
    sections = sorted(set(q["section"] for q in questions))
    return render_template("admin.html", questions=questions, sections=sections,
                           edit_question=target)


@app.route("/admin/questions/<int:qid>/delete", methods=["POST"])
def admin_delete_question(qid):
    """حذف سؤال من questions.json."""
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    questions = load_questions()
    questions = [q for q in questions if q["id"] != qid]
    save_questions(questions)

    sections = sorted(set(q["section"] for q in questions))
    return render_template("admin.html", questions=questions, sections=sections,
                           form_success="تم حذف السؤال بنجاح")


@app.route("/admin/logout")
def admin_logout():
    """تسجيل خروج الإدارة."""
    session.pop("is_admin", None)
    return redirect(url_for("admin_login"))


@app.route("/admin/answers")
def admin_answers():
    """عرض قائمة كل الطلاب الذين أكملوا الاختبار (للأدمن فقط).

    يدمج بيانات جدول results مع التحقق من وجود تفاصيل في answer_details.
    الطلاب القدامى بدون تفاصيل يظهرون لكن بدون رابط مراجعة.
    """
    if not session.get("is_admin"):
        return redirect(url_for("admin_login", next=request.path))

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """SELECT r.name AS student_name,
                      r.correct AS correct_count,
                      r.total AS total_count,
                      r.percentage,
                      r.date,
                      CASE WHEN a.cnt > 0 THEN 1 ELSE 0 END AS has_details
               FROM results r
               LEFT JOIN (
                   SELECT student_name, date, COUNT(*) AS cnt
                   FROM answer_details
                   GROUP BY student_name, date
               ) a ON a.student_name = r.name AND a.date = r.date
               WHERE r.status = 'completed'
               ORDER BY r.date DESC"""
        ).fetchall()
        students = [dict(row) for row in rows]
    finally:
        conn.close()

    return render_template("admin_answers.html", students=students)


@app.route("/admin/answers/detail")
def admin_answers_detail():
    """عرض تفاصيل إجابات طالب محدد (للأدمن فقط)."""
    if not session.get("is_admin"):
        return redirect(url_for("admin_login", next=request.full_path))

    name = request.args.get("name", "").strip()
    date = request.args.get("date", "").strip()
    if not name or not date:
        return redirect(url_for("admin_answers"))

    details = load_answer_details(name, date)
    return render_template(
        "admin_answers.html", details=details, student_name=name, student_date=date
    )


@app.route("/admin/answers/delete", methods=["POST"])
def admin_answers_delete():
    """حذف طالب وكل تفاصيل إجاباته (للأدمن فقط)."""
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    name = request.form.get("name", "").strip()
    date = request.form.get("date", "").strip()
    if not name or not date:
        return redirect(url_for("admin_answers"))

    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute(
            "DELETE FROM results WHERE name = ? AND date = ?",
            (name, date),
        )
        conn.execute(
            "DELETE FROM answer_details WHERE student_name = ? AND date = ?",
            (name, date),
        )
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("admin_answers"))


def _build_question_from_form(req, qid):
    """بناء قاموس سؤال من بيانات النموذج.

    تُرجع None إذا كانت الحقول الإلزامية ناقصة.
    """
    section = req.form.get("section", "").strip()
    question_text = req.form.get("question", "").strip()
    code = req.form.get("code", "").strip()
    image = req.form.get("image", "").strip()
    correct = req.form.get("correct_answer", "").strip()

    options = {}
    for letter in ("أ", "ب", "ج", "د"):
        val = req.form.get(f"option_{letter}", "").strip()
        if val:
            options[letter] = val

    # التحقق من اكتمال الحقول الإلزامية
    if not question_text or len(options) < 2 or correct not in options:
        return None

    return {
        "id": qid,
        "section": section if section else "قسم عام",
        "question": question_text,
        "code": code if code else None,
        "image": image if image else None,
        "options": options,
        "correct_answer": correct,
    }


# ─── تسجيل الخروج ───
@app.route("/logout")
def logout():
    """تسجيل خروج الطالب مع الحفاظ على جلسة الأدمن."""
    session.pop("name", None)
    session.pop("submitted", None)
    session.pop("resume_code", None)
    session.pop("result_token", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=5000)
