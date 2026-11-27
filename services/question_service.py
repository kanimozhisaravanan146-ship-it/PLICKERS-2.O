"""
RotQR Question Service

Handles question creation, retrieval,
activation, and deactivation.
"""

import database


def create_question(
    question_text,
    option_a,
    option_b,
    option_c,
    option_d,
    correct_answer
):
    """Create a new MCQ question."""

    # Validate question text
    if not question_text or not question_text.strip():
        raise ValueError("Question text cannot be empty.")

    # Validate options
    options = {
        "A": option_a,
        "B": option_b,
        "C": option_c,
        "D": option_d
    }

    for label, option_text in options.items():
        if not option_text or not option_text.strip():
            raise ValueError(f"Option {label} cannot be empty.")

    # Validate correct answer
    correct_answer = correct_answer.strip().upper()

    if correct_answer not in ("A", "B", "C", "D"):
        raise ValueError("Correct answer must be A, B, C, or D.")

    # Store question using database.py
    question_id = database.add_question(
        question_text.strip(),
        option_a.strip(),
        option_b.strip(),
        option_c.strip(),
        option_d.strip(),
        correct_answer
    )

    return question_id


def get_all_questions():
    """Get all questions from the database."""

    return database.get_questions()


def get_question_by_id(question_id):
    """Get a specific question using its ID."""

    question = database.get_question_by_id(question_id)

    if question is None:
        raise ValueError("Question not found.")

    return question


def activate_question(question_id):
    """Activate a question for students to answer."""

    success = database.activate_question(question_id)

    if not success:
        raise ValueError("Question not found.")

    return True


def get_active_question():
    """Get the currently active question."""

    return database.get_active_question()


def deactivate_question():
    """Deactivate the currently active question."""

    active_question = database.get_active_question()

    if active_question is None:
        return False

    with database.get_connection() as connection:
        connection.execute("""
            UPDATE questions
            SET is_active = 0
            WHERE is_active = 1
        """)

    return True