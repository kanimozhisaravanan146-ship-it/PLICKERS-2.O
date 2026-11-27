"""
RotQR database module
Stores students, questions, and student responses.
"""

import sqlite3
import secrets
from pathlib import Path
from contextlib import contextmanager


# Database file will be created in the same folder as this file.
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "rotqr.db"


@contextmanager
def get_connection():
    """
    Open a database connection.
    Automatically commits if successful and rolls back if an error occurs.
    """
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    # Enable foreign-key validation for this connection.
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db():
    """Create the required tables if they do not already exist."""

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                student_token TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_text TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_answer TEXT NOT NULL
                    CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
                is_active INTEGER NOT NULL DEFAULT 0
                    CHECK (is_active IN (0, 1)),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                answer TEXT NOT NULL
                    CHECK (answer IN ('A', 'B', 'C', 'D')),
                is_correct INTEGER NOT NULL
                    CHECK (is_correct IN (0, 1)),
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (student_id)
                    REFERENCES students(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (question_id)
                    REFERENCES questions(id)
                    ON DELETE CASCADE,

                UNIQUE (student_id, question_id)
            )
        """)

        # Ensure only one question can be active at a time.
        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
            one_active_question
            ON questions(is_active)
            WHERE is_active = 1
        """)


# --------------------------------------------------
# STUDENT FUNCTIONS
# --------------------------------------------------

def add_student(student_name, student_token=None):
    """
    Add a student to the database.

    If no token is provided, generate a unique QR token.
    Returns the new student's database ID.
    """

    student_name = student_name.strip()

    if not student_name:
        raise ValueError("Student name cannot be empty.")

    if student_token is None:
        student_token = secrets.token_urlsafe(16)

    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO students (student_name, student_token)
            VALUES (?, ?)
        """, (student_name, student_token))

        return cursor.lastrowid


def get_students():
    """Return all registered students."""

    with get_connection() as connection:
        rows = connection.execute("""
            SELECT id, student_name, student_token, created_at
            FROM students
            ORDER BY student_name
        """).fetchall()

        return [dict(row) for row in rows]


def get_student_by_token(student_token):
    """Find a student using the token stored inside their QR code."""

    with get_connection() as connection:
        row = connection.execute("""
            SELECT id, student_name, student_token
            FROM students
            WHERE student_token = ?
        """, (student_token,)).fetchone()

        return dict(row) if row else None


# --------------------------------------------------
# QUESTION FUNCTIONS
# --------------------------------------------------

def add_question(
    question_text,
    option_a,
    option_b,
    option_c,
    option_d,
    correct_answer
):
    """
    Add a new MCQ question.
    New questions are inactive by default.
    Returns the new question ID.
    """

    question_text = question_text.strip()
    correct_answer = correct_answer.strip().upper()

    if not question_text:
        raise ValueError("Question text cannot be empty.")

    if correct_answer not in ("A", "B", "C", "D"):
        raise ValueError("Correct answer must be A, B, C, or D.")

    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO questions (
                question_text,
                option_a,
                option_b,
                option_c,
                option_d,
                correct_answer
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            question_text,
            option_a,
            option_b,
            option_c,
            option_d,
            correct_answer
        ))

        return cursor.lastrowid


def get_questions():
    """Return all questions."""

    with get_connection() as connection:
        rows = connection.execute("""
            SELECT *
            FROM questions
            ORDER BY id DESC
        """).fetchall()

        return [dict(row) for row in rows]


def get_question_by_id(question_id):
    """Return one question using its ID."""

    with get_connection() as connection:
        row = connection.execute("""
            SELECT *
            FROM questions
            WHERE id = ?
        """, (question_id,)).fetchone()

        return dict(row) if row else None


def activate_question(question_id):
    """
    Activate the selected question and deactivate all others.
    Returns True if the question exists and was activated.
    """

    with get_connection() as connection:

        question = connection.execute("""
            SELECT id
            FROM questions
            WHERE id = ?
        """, (question_id,)).fetchone()

        if question is None:
            return False

        # Deactivate the current active question first.
        connection.execute("""
            UPDATE questions
            SET is_active = 0
            WHERE is_active = 1
        """)

        # Activate the selected question.
        connection.execute("""
            UPDATE questions
            SET is_active = 1
            WHERE id = ?
        """, (question_id,))

        return True


def get_active_question():
    """Return the currently active question, if any."""

    with get_connection() as connection:
        row = connection.execute("""
            SELECT *
            FROM questions
            WHERE is_active = 1
            LIMIT 1
        """).fetchone()

        return dict(row) if row else None


# --------------------------------------------------
# RESPONSE FUNCTIONS
# --------------------------------------------------

def get_student_response(student_id, question_id):
    """Check whether a student has already answered a question."""

    with get_connection() as connection:
        row = connection.execute("""
            SELECT *
            FROM responses
            WHERE student_id = ?
              AND question_id = ?
        """, (student_id, question_id)).fetchone()

        return dict(row) if row else None


def save_response(student_id, question_id, answer):
    """
    Save a student's answer.

    Returns:
        True  -> response saved successfully
        False -> student already answered this question

    Correctness is calculated using the question's answer key.
    """

    answer = answer.strip().upper()

    if answer not in ("A", "B", "C", "D"):
        raise ValueError("Answer must be A, B, C, or D.")

    with get_connection() as connection:

        question = connection.execute("""
            SELECT correct_answer
            FROM questions
            WHERE id = ?
        """, (question_id,)).fetchone()

        if question is None:
            raise ValueError("Question does not exist.")

        is_correct = int(answer == question["correct_answer"])

        cursor = connection.execute("""
            INSERT OR IGNORE INTO responses (
                student_id,
                question_id,
                answer,
                is_correct
            )
            VALUES (?, ?, ?, ?)
        """, (
            student_id,
            question_id,
            answer,
            is_correct
        ))

        # INSERT OR IGNORE returns rowcount 0 for duplicates.
        return cursor.rowcount == 1


# --------------------------------------------------
# RESULT FUNCTIONS
# --------------------------------------------------

def get_question_results(question_id):
    """Return all responses submitted for a question."""

    with get_connection() as connection:
        rows = connection.execute("""
            SELECT
                students.id AS student_id,
                students.student_name,
                responses.answer,
                responses.is_correct,
                responses.submitted_at
            FROM responses
            JOIN students
                ON students.id = responses.student_id
            WHERE responses.question_id = ?
            ORDER BY students.student_name
        """, (question_id,)).fetchall()

        return [dict(row) for row in rows]


def get_active_question_results():
    """
    Return response counts for the active question.

    Includes:
        total students
        submitted responses
        correct responses
        incorrect responses
    """

    active_question = get_active_question()

    if active_question is None:
        return None

    question_id = active_question["id"]

    with get_connection() as connection:

        total_students = connection.execute("""
            SELECT COUNT(*) AS total
            FROM students
        """).fetchone()["total"]

        result = connection.execute("""
            SELECT
                COUNT(*) AS submitted,
                SUM(is_correct = 1) AS correct,
                SUM(is_correct = 0) AS incorrect
            FROM responses
            WHERE question_id = ?
        """, (question_id,)).fetchone()

        return {
            "question": active_question,
            "total_students": total_students,
            "submitted": result["submitted"] or 0,
            "correct": result["correct"] or 0,
            "incorrect": result["incorrect"] or 0
        }


# --------------------------------------------------
# INITIALIZE DATABASE
# --------------------------------------------------

if __name__ == "__main__":
    init_db()
    print("RotQR database initialized successfully.")