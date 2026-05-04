import os
import random
import sqlite3

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-secret-key")
app.config["SESSION_PERMANENT"] = False
MANAGER_ACCESS_CODE = os.environ.get("MANAGER_ACCESS_CODE", "JNV-MANAGER-2026")


@app.context_processor
def inject_login_state():
    return {
        "is_student_logged_in": "user_id" in session,
        "logged_student_name": session.get("user_name"),
        "is_manager_logged_in": session.get("manager_verified", False),
        "logged_manager_name": session.get("manager_name"),
    }


def get_db_connection():
    conn = sqlite3.connect("quiz.db")
    conn.row_factory = sqlite3.Row
    return conn


def generate_otp():
    return str(random.randint(100000, 999999))


def ensure_database_schema(conn):
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    
    # Create questions table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            topic TEXT,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            solution TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    
    # Create test_attempts table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS test_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            correct_answers INTEGER NOT NULL,
            wrong_answers INTEGER NOT NULL,
            unanswered INTEGER NOT NULL,
            score REAL NOT NULL,
            max_score REAL NOT NULL,
            percentage REAL NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    
    # Create test_series table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS test_series (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject TEXT NOT NULL,
            section_name TEXT,
            unit_name TEXT,
            chapter_name TEXT,
            topic TEXT,
            description TEXT,
            time_limit_minutes INTEGER DEFAULT 30,
            positive_marks REAL DEFAULT 1,
            negative_marks REAL DEFAULT 0,
            cutoff_marks REAL DEFAULT 0,
            manager_name TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    
    # Create test_series_questions table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS test_series_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_series_id INTEGER NOT NULL,
            question_order INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            solution TEXT,
            FOREIGN KEY (test_series_id) REFERENCES test_series(id)
        )
        """
    )
    
    # Create test_series_attempts table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS test_series_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_series_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            correct_answers INTEGER NOT NULL,
            wrong_answers INTEGER NOT NULL,
            unanswered INTEGER NOT NULL,
            attempted INTEGER NOT NULL,
            skipped INTEGER NOT NULL,
            positive_score REAL NOT NULL,
            negative_score REAL NOT NULL,
            score REAL NOT NULL,
            max_score REAL NOT NULL,
            percentage REAL NOT NULL,
            cutoff_marks REAL NOT NULL,
            passed INTEGER NOT NULL,
            time_limit_minutes INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (test_series_id) REFERENCES test_series(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    
    # Create test_series_answers table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS test_series_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attempt_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            selected_answer TEXT,
            is_correct INTEGER NOT NULL,
            marks REAL NOT NULL,
            FOREIGN KEY (attempt_id) REFERENCES test_series_attempts(id),
            FOREIGN KEY (question_id) REFERENCES test_series_questions(id)
        )
        """
    )
    
    conn.commit()


def to_float(value):
    return float(value or 0)


def load_manager_tests(cursor):
    cursor.execute(
        """
        SELECT
            ts.id, ts.title, ts.subject, ts.section_name, ts.unit_name, ts.chapter_name, ts.topic,
            ts.time_limit_minutes, ts.positive_marks, ts.negative_marks, ts.cutoff_marks,
            COUNT(tsq.id) AS question_count
        FROM test_series ts
        LEFT JOIN test_series_questions tsq ON tsq.test_series_id = ts.id
        GROUP BY ts.id, ts.title, ts.subject, ts.section_name, ts.unit_name, ts.chapter_name, ts.topic,
            ts.time_limit_minutes, ts.positive_marks, ts.negative_marks, ts.cutoff_marks, ts.created_at
        ORDER BY ts.created_at DESC
        """
    )
    return cursor.fetchall()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, email, password_hash FROM users WHERE email = ?",
                (email,),
            )
            user = cursor.fetchone()
            conn.close()
        except Exception as e:
            error = "Database connection failed."
            return render_template("login.html", error=error)

        if user and check_password_hash(user["password_hash"], password):
            session["pending_user_id"] = user["id"]
            session["pending_user_name"] = user["name"]
            session["student_otp"] = generate_otp()
            return redirect(url_for("verify_student_otp"))

        error = "Invalid email or password."

    return render_template("login.html", error=error)


@app.route("/verify-student-otp", methods=["GET", "POST"])
def verify_student_otp():
    if "pending_user_id" not in session:
        return redirect(url_for("login"))

    error = None

    if request.method == "POST":
        entered_otp = request.form["otp"].strip()

        if entered_otp == session.get("student_otp"):
            session["user_id"] = session.pop("pending_user_id")
            session["user_name"] = session.pop("pending_user_name")
            session.pop("student_otp", None)
            return redirect(url_for("test_series"))

        error = "Invalid OTP. Please try again."

    return render_template(
        "verify_otp.html",
        title="Student OTP Verification",
        heading="Verify Student Login",
        otp=session.get("student_otp"),
        action_url=url_for("verify_student_otp"),
        error=error,
    )


@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None

    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        password_hash = generate_password_hash(password)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash),
            )
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            error = "This email is already registered."
        except Exception:
            error = "Database connection failed."

    return render_template("signup.html", error=error)


@app.route("/questions")
def questions():
    if "user_id" not in session:
        return redirect(url_for("login"))

    error = None
    quiz_questions = []
    subjects = []
    topics = []
    selected_subject = request.args.get("subject", "").strip()
    selected_topic = request.args.get("topic", "").strip()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT subject FROM questions WHERE subject IS NOT NULL ORDER BY subject")
        subjects = [row["subject"] for row in cursor.fetchall()]

        if selected_subject:
            cursor.execute(
                "SELECT DISTINCT topic FROM questions WHERE subject = ? AND topic IS NOT NULL ORDER BY topic",
                (selected_subject,),
            )
        else:
            cursor.execute("SELECT DISTINCT topic FROM questions WHERE topic IS NOT NULL ORDER BY topic")
        topics = [row["topic"] for row in cursor.fetchall()]

        query = """
            SELECT id, subject, topic, question_text, option_a, option_b, option_c, option_d
            FROM questions
            WHERE 1 = 1
        """
        params = []

        if selected_subject:
            query += " AND subject = ?"
            params.append(selected_subject)

        if selected_topic:
            query += " AND topic = ?"
            params.append(selected_topic)

        query += " ORDER BY subject, topic, id"
        cursor.execute(query, params)
        quiz_questions = cursor.fetchall()
        conn.close()
    except Exception:
        error = "Could not load questions from database."

    return render_template(
        "questions.html",
        questions=quiz_questions,
        subjects=subjects,
        topics=topics,
        selected_subject=selected_subject,
        selected_topic=selected_topic,
        error=error,
        user_name=session.get("user_name"),
    )


@app.route("/submit-test", methods=["POST"])
def submit_test():
    if "user_id" not in session:
        return redirect(url_for("login"))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        question_ids = [int(question_id) for question_id in request.form.getlist("test_question_id")]

        if not question_ids:
            return render_template(
                "analysis.html",
                error="No questions were selected for this test.",
                result=None,
            )

        placeholders = ", ".join("?" * len(question_ids))
        cursor.execute(
            f"SELECT id, correct_answer FROM questions WHERE id IN ({placeholders}) ORDER BY id",
            question_ids,
        )
        correct_answers = cursor.fetchall()
    except Exception:
        return render_template(
            "analysis.html",
            error="Could not check answers from database.",
            result=None,
        )

    total_questions = len(correct_answers)
    correct = 0
    wrong = 0
    unanswered = 0

    for question in correct_answers:
        selected = request.form.get(f"question_{question['id']}")

        if not selected:
            unanswered += 1
        elif selected == question["correct_answer"]:
            correct += 1
        else:
            wrong += 1

    score = correct
    max_score = total_questions
    percentage = round((score / max_score) * 100, 2) if max_score else 0

    result = {
        "total_questions": total_questions,
        "correct": correct,
        "wrong": wrong,
        "unanswered": unanswered,
        "score": score,
        "max_score": max_score,
        "percentage": percentage,
    }

    try:
        cursor.execute(
            """
            INSERT INTO test_attempts
                (user_id, total_questions, correct_answers, wrong_answers, unanswered, score, max_score, percentage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (session["user_id"], total_questions, correct, wrong, unanswered, score, max_score, percentage),
        )
        attempt_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return redirect(url_for("analysis", attempt_id=attempt_id))
    except Exception:
        conn.close()
        return render_template("analysis.html", result=result, error=None)


@app.route("/analysis/<int:attempt_id>")
def analysis(attempt_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    error = None
    result = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT total_questions, correct_answers, wrong_answers, unanswered, score, max_score, percentage, created_at
            FROM test_attempts
            WHERE id = ? AND user_id = ?
            """,
            (attempt_id, session["user_id"]),
        )
        attempt = cursor.fetchone()
        conn.close()

        if attempt:
            result = {
                "total_questions": attempt["total_questions"],
                "correct": attempt["correct_answers"],
                "wrong": attempt["wrong_answers"],
                "unanswered": attempt["unanswered"],
                "score": attempt["score"],
                "max_score": attempt["max_score"],
                "percentage": attempt["percentage"],
                "created_at": attempt["created_at"],
            }
        else:
            error = "Result not found."
    except Exception:
        error = "Could not load test analysis from database."

    return render_template("analysis.html", result=result, error=error)


@app.route("/test-series")
def test_series():
    if "user_id" not in session:
        return redirect(url_for("login"))

    tests = []
    history = []
    error = None

    try:
        conn = get_db_connection()
        ensure_database_schema(conn)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                ts.id, ts.title, ts.subject, ts.section_name, ts.unit_name, ts.chapter_name, ts.topic,
                ts.time_limit_minutes, ts.positive_marks, ts.negative_marks, ts.cutoff_marks,
                COUNT(tsq.id) AS question_count
            FROM test_series ts
            LEFT JOIN test_series_questions tsq ON tsq.test_series_id = ts.id
            GROUP BY ts.id, ts.title, ts.subject, ts.section_name, ts.unit_name, ts.chapter_name, ts.topic,
                ts.time_limit_minutes, ts.positive_marks, ts.negative_marks, ts.cutoff_marks, ts.created_at
            ORDER BY ts.created_at DESC
            """
        )
        tests = cursor.fetchall()
        cursor.execute(
            """
            SELECT tsa.id, tsa.score, tsa.max_score, tsa.percentage, tsa.created_at, ts.title
            FROM test_series_attempts tsa
            JOIN test_series ts ON ts.id = tsa.test_series_id
            WHERE tsa.user_id = ?
            ORDER BY tsa.created_at DESC
            LIMIT 5
            """,
            (session["user_id"],),
        )
        history = cursor.fetchall()
        conn.close()
    except Exception:
        error = "Could not load test series from database."

    return render_template(
        "test_series.html",
        tests=tests,
        history=history,
        error=error,
        user_name=session.get("user_name"),
    )


@app.route("/test-series/<int:test_id>")
def attempt_series(test_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    test = None
    questions_list = []
    error = None

    try:
        conn = get_db_connection()
        ensure_database_schema(conn)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM test_series WHERE id = ?", (test_id,))
        test = cursor.fetchone()
        cursor.execute(
            """
            SELECT id, question_order, question_text, option_a, option_b, option_c, option_d
            FROM test_series_questions
            WHERE test_series_id = ?
            ORDER BY question_order, id
            """,
            (test_id,),
        )
        questions_list = cursor.fetchall()
        conn.close()
    except Exception:
        error = "Could not open this test series."

    if not test and not error:
        error = "Test series not found."

    return render_template("test_attempt.html", test=test, questions=questions_list, error=error)


@app.route("/test-series/<int:test_id>/submit", methods=["POST"])
def submit_series_test(test_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    try:
        conn = get_db_connection()
        ensure_database_schema(conn)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM test_series WHERE id = ?", (test_id,))
        test = cursor.fetchone()
        cursor.execute(
            """
            SELECT id, correct_answer
            FROM test_series_questions
            WHERE test_series_id = ?
            ORDER BY question_order, id
            """,
            (test_id,),
        )
        questions_list = cursor.fetchall()

        if not test or not questions_list:
            conn.close()
            return render_template("analysis.html", result=None, error="No questions found in this test.")

        positive_marks = to_float(test["positive_marks"])
        negative_marks = to_float(test["negative_marks"])
        cutoff_marks = to_float(test["cutoff_marks"])
        total_questions = len(questions_list)
        correct = 0
        wrong = 0
        unanswered = 0
        answer_rows = []

        for question in questions_list:
            selected = request.form.get(f"question_{question['id']}")
            marks = 0
            is_correct = 0

            if not selected:
                unanswered += 1
            elif selected == question["correct_answer"]:
                correct += 1
                is_correct = 1
                marks = positive_marks
            else:
                wrong += 1
                marks = -negative_marks

            answer_rows.append((question["id"], selected, is_correct, marks))

        attempted = correct + wrong
        skipped = unanswered
        positive_score = correct * positive_marks
        negative_score = wrong * negative_marks
        score = positive_score - negative_score
        max_score = total_questions * positive_marks
        percentage = round((score / max_score) * 100, 2) if max_score else 0
        passed = 1 if score >= cutoff_marks else 0

        cursor.execute(
            """
            INSERT INTO test_series_attempts
                (test_series_id, user_id, total_questions, correct_answers, wrong_answers, unanswered,
                 attempted, skipped, positive_score, negative_score, score, max_score, percentage,
                 cutoff_marks, passed, time_limit_minutes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (test_id, session["user_id"], total_questions, correct, wrong, unanswered, attempted, skipped,
             positive_score, negative_score, score, max_score, percentage, cutoff_marks, passed,
             int(test["time_limit_minutes"])),
        )
        attempt_id = cursor.lastrowid

        for question_id, selected, is_correct, marks in answer_rows:
            cursor.execute(
                """
                INSERT INTO test_series_answers (attempt_id, question_id, selected_answer, is_correct, marks)
                VALUES (?, ?, ?, ?, ?)
                """,
                (attempt_id, question_id, selected, is_correct, marks),
            )

        conn.commit()
        conn.close()
        return redirect(url_for("series_analysis", attempt_id=attempt_id))
    except Exception:
        return render_template("analysis.html", result=None, error="Could not submit test series answers.")


@app.route("/series-analysis/<int:attempt_id>")
def series_analysis(attempt_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    result = None
    answers = []
    error = None

    try:
        conn = get_db_connection()
        ensure_database_schema(conn)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT tsa.*, ts.title, ts.subject, ts.section_name, ts.unit_name, ts.chapter_name, ts.topic
            FROM test_series_attempts tsa
            JOIN test_series ts ON ts.id = tsa.test_series_id
            WHERE tsa.id = ? AND tsa.user_id = ?
            """,
            (attempt_id, session["user_id"]),
        )
        attempt = cursor.fetchone()

        if attempt:
            cursor.execute(
                """
                SELECT COUNT(*) + 1 AS rank_no
                FROM test_series_attempts
                WHERE test_series_id = ? AND score > ?
                """,
                (attempt["test_series_id"], attempt["score"]),
            )
            rank_no = cursor.fetchone()["rank_no"]
            cursor.execute(
                "SELECT COUNT(*) AS total_attempts FROM test_series_attempts WHERE test_series_id = ?",
                (attempt["test_series_id"],),
            )
            total_attempts = cursor.fetchone()["total_attempts"]
            cursor.execute(
                """
                SELECT
                    tsq.question_order, tsq.question_text, tsq.option_a, tsq.option_b, tsq.option_c, tsq.option_d,
                    tsq.correct_answer, tsq.solution, tsa.selected_answer, tsa.is_correct, tsa.marks
                FROM test_series_answers tsa
                JOIN test_series_questions tsq ON tsq.id = tsa.question_id
                WHERE tsa.attempt_id = ?
                ORDER BY tsq.question_order, tsq.id
                """,
                (attempt_id,),
            )
            answers = cursor.fetchall()
            result = {
                "series_mode": True,
                "attempt_id": attempt["id"],
                "test_title": attempt["title"],
                "subject": attempt["subject"],
                "section_name": attempt["section_name"],
                "unit_name": attempt["unit_name"],
                "chapter_name": attempt["chapter_name"],
                "topic": attempt["topic"],
                "total_questions": attempt["total_questions"],
                "correct": attempt["correct_answers"],
                "wrong": attempt["wrong_answers"],
                "unanswered": attempt["unanswered"],
                "attempted": attempt["attempted"],
                "skipped": attempt["skipped"],
                "positive_score": to_float(attempt["positive_score"]),
                "negative_score": to_float(attempt["negative_score"]),
                "score": to_float(attempt["score"]),
                "max_score": to_float(attempt["max_score"]),
                "percentage": to_float(attempt["percentage"]),
                "cutoff_marks": to_float(attempt["cutoff_marks"]),
                "passed": attempt["passed"],
                "rank": rank_no,
                "total_attempts": total_attempts,
                "created_at": attempt["created_at"],
            }
        else:
            error = "Result not found."
        conn.close()
    except Exception:
        error = "Could not load detailed test analysis."

    return render_template("analysis.html", result=result, answers=answers, error=error)


@app.route("/my-results")
def my_results():
    if "user_id" not in session:
        return redirect(url_for("login"))

    attempts = []
    error = None

    try:
        conn = get_db_connection()
        ensure_database_schema(conn)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT tsa.id, tsa.score, tsa.max_score, tsa.percentage, tsa.correct_answers, tsa.wrong_answers,
                   tsa.unanswered, tsa.cutoff_marks, tsa.passed, tsa.created_at, ts.title, ts.subject, ts.topic
            FROM test_series_attempts tsa
            JOIN test_series ts ON ts.id = tsa.test_series_id
            WHERE tsa.user_id = ?
            ORDER BY tsa.created_at DESC
            """,
            (session["user_id"],),
        )
        attempts = cursor.fetchall()
        conn.close()
    except Exception:
        error = "Could not load your result history."

    return render_template("history.html", attempts=attempts, error=error, user_name=session.get("user_name"))


@app.route("/manager", methods=["GET", "POST"])
def manager():
    if not session.get("manager_verified"):
        return redirect(url_for("manager_login"))

    message = None
    error = None
    manager_tests = []

    if request.method == "POST":
        action_type = request.form.get("action_type", "question_bank")
        subject = request.form["subject"].strip()
        topic = request.form["topic"].strip()
        question_count = int(request.form.get("question_count", 1))
        uploaded = 0

        try:
            conn = get_db_connection()
            ensure_database_schema(conn)
            cursor = conn.cursor()

            if action_type == "test_series":
                cursor.execute(
                    """
                    INSERT INTO test_series
                        (title, subject, section_name, unit_name, chapter_name, topic, description,
                         time_limit_minutes, positive_marks, negative_marks, cutoff_marks, manager_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (request.form["title"].strip(), subject,
                     request.form.get("section_name", "").strip(),
                     request.form.get("unit_name", "").strip(),
                     request.form.get("chapter_name", "").strip(),
                     topic,
                     request.form.get("description", "").strip(),
                     int(request.form.get("time_limit_minutes", 30)),
                     float(request.form.get("positive_marks", 1)),
                     float(request.form.get("negative_marks", 0)),
                     float(request.form.get("cutoff_marks", 0)),
                     session.get("manager_name")),
                )
                test_series_id = cursor.lastrowid

                for index in range(1, question_count + 1):
                    question_text = request.form.get(f"question_text_{index}", "").strip()
                    option_a = request.form.get(f"option_a_{index}", "").strip()
                    option_b = request.form.get(f"option_b_{index}", "").strip()
                    option_c = request.form.get(f"option_c_{index}", "").strip()
                    option_d = request.form.get(f"option_d_{index}", "").strip()
                    correct_answer = request.form.get(f"correct_answer_{index}", "")
                    solution = request.form.get(f"solution_{index}", "").strip()

                    if not question_text:
                        continue

                    cursor.execute(
                        """
                        INSERT INTO test_series_questions
                            (test_series_id, question_order, question_text, option_a, option_b, option_c, option_d, correct_answer, solution)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (test_series_id, index, question_text, option_a, option_b, option_c, option_d, correct_answer, solution),
                    )
                    uploaded += 1

                conn.commit()
                manager_tests = load_manager_tests(cursor)
                conn.close()
                message = f"Test series created with {uploaded} question."
                return render_template("manager.html", message=message, error=error, manager_tests=manager_tests)

            for index in range(1, question_count + 1):
                question_text = request.form.get(f"question_text_{index}", "").strip()
                option_a = request.form.get(f"option_a_{index}", "").strip()
                option_b = request.form.get(f"option_b_{index}", "").strip()
                option_c = request.form.get(f"option_c_{index}", "").strip()
                option_d = request.form.get(f"option_d_{index}", "").strip()
                correct_answer = request.form.get(f"correct_answer_{index}", "")
                solution = request.form.get(f"solution_{index}", "").strip()

                if not question_text:
                    continue

                cursor.execute(
                    """
                    INSERT INTO questions
                        (subject, topic, question_text, option_a, option_b, option_c, option_d, correct_answer, solution)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (subject, topic, question_text, option_a, option_b, option_c, option_d, correct_answer, solution),
                )
                uploaded += 1

            conn.commit()
            manager_tests = load_manager_tests(cursor)
            conn.close()
            message = f"{uploaded} question uploaded successfully."
        except Exception:
            error = "Question upload failed. Please check your data."

    if request.method == "GET":
        try:
            conn = get_db_connection()
            ensure_database_schema(conn)
            cursor = conn.cursor()
            manager_tests = load_manager_tests(cursor)
            conn.close()
        except Exception:
            error = "Could not load created test papers."

    return render_template("manager.html", message=message, error=error, manager_tests=manager_tests)


@app.route("/manager/test-series/<int:test_id>/edit", methods=["GET", "POST"])
def edit_test_series(test_id):
    if not session.get("manager_verified"):
        return redirect(url_for("manager_login"))

    message = None
    error = None
    edit_test = None
    edit_questions = []
    manager_tests = []

    try:
        conn = get_db_connection()
        ensure_database_schema(conn)
        cursor = conn.cursor()

        if request.method == "POST":
            subject = request.form["subject"].strip()
            topic = request.form["topic"].strip()
            question_count = int(request.form.get("question_count", 1))

            cursor.execute(
                """
                UPDATE test_series
                SET title = ?, subject = ?, section_name = ?, unit_name = ?, chapter_name = ?, topic = ?,
                    description = ?, time_limit_minutes = ?, positive_marks = ?, negative_marks = ?, cutoff_marks = ?
                WHERE id = ?
                """,
                (request.form["title"].strip(), subject,
                 request.form.get("section_name", "").strip(),
                 request.form.get("unit_name", "").strip(),
                 request.form.get("chapter_name", "").strip(),
                 topic,
                 request.form.get("description", "").strip(),
                 int(request.form.get("time_limit_minutes", 30)),
                 float(request.form.get("positive_marks", 1)),
                 float(request.form.get("negative_marks", 0)),
                 float(request.form.get("cutoff_marks", 0)),
                 test_id),
            )

            saved = 0
            for index in range(1, question_count + 1):
                question_text = request.form.get(f"question_text_{index}", "").strip()
                option_a = request.form.get(f"option_a_{index}", "").strip()
                option_b = request.form.get(f"option_b_{index}", "").strip()
                option_c = request.form.get(f"option_c_{index}", "").strip()
                option_d = request.form.get(f"option_d_{index}", "").strip()
                correct_answer = request.form.get(f"correct_answer_{index}", "")
                solution = request.form.get(f"solution_{index}", "").strip()
                question_id = request.form.get(f"question_id_{index}", "").strip()

                if not question_text:
                    continue

                if question_id:
                    cursor.execute(
                        """
                        UPDATE test_series_questions
                        SET question_order = ?, question_text = ?, option_a = ?, option_b = ?, option_c = ?,
                            option_d = ?, correct_answer = ?, solution = ?
                        WHERE id = ? AND test_series_id = ?
                        """,
                        (index, question_text, option_a, option_b, option_c, option_d, correct_answer, solution,
                         int(question_id), test_id),
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO test_series_questions
                            (test_series_id, question_order, question_text, option_a, option_b, option_c, option_d, correct_answer, solution)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (test_id, index, question_text, option_a, option_b, option_c, option_d, correct_answer, solution),
                    )
                saved += 1

            conn.commit()
            message = f"Test paper updated with {saved} question."

        cursor.execute("SELECT * FROM test_series WHERE id = ?", (test_id,))
        edit_test = cursor.fetchone()
        cursor.execute(
            """
            SELECT *
            FROM test_series_questions
            WHERE test_series_id = ?
            ORDER BY question_order, id
            """,
            (test_id,),
        )
        edit_questions = cursor.fetchall()
        manager_tests = load_manager_tests(cursor)
        conn.close()
    except Exception:
        error = "Could not edit this test paper. Check database connection."

    return render_template(
        "manager.html",
        message=message,
        error=error,
        manager_tests=manager_tests,
        edit_test=edit_test,
        edit_questions=edit_questions,
    )


@app.route("/manager-login", methods=["GET", "POST"])
def manager_login():
    error = None

    if request.method == "POST":
        manager_name = request.form["manager_name"].strip()
        access_code = request.form["access_code"].strip()

        if access_code == MANAGER_ACCESS_CODE:
            session["pending_manager_name"] = manager_name
            session["manager_otp"] = generate_otp()
            return redirect(url_for("verify_manager_otp"))

        error = "Invalid manager access code."

    return render_template("manager_login.html", error=error)


@app.route("/verify-manager-otp", methods=["GET", "POST"])
def verify_manager_otp():
    if "pending_manager_name" not in session:
        return redirect(url_for("manager_login"))

    error = None

    if request.method == "POST":
        entered_otp = request.form["otp"].strip()

        if entered_otp == session.get("manager_otp"):
            session["manager_verified"] = True
            session["manager_name"] = session.pop("pending_manager_name")
            session.pop("manager_otp", None)
            return redirect(url_for("manager"))

        error = "Invalid OTP. Please try again."

    return render_template(
        "verify_otp.html",
        title="Manager OTP Verification",
        heading="Verify Manager Access",
        otp=session.get("manager_otp"),
        action_url=url_for("verify_manager_otp"),
        error=error,
    )


@app.route("/manager-logout")
def manager_logout():
    session.pop("manager_verified", None)
    session.pop("manager_name", None)
    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=port, host="0.0.0.0", use_reloader=False)

