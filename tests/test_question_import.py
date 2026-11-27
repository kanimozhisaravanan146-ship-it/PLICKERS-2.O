
import pytest

from services.question_service import parse_question_rows


def test_valid_question_import():

    questions = [
        {
            "question_id": "Q001",
            "question_text": "What is Python?",
            "correct_answer": "A"
        },
        {
            "question_id": "Q002",
            "question_text": "What is Java?",
            "correct_answer": "B"
        }
    ]

    result = parse_question_rows(questions)

    assert len(result) == 2


def test_question_id_exists():

    questions = [
        {
            "question_id": "Q001",
            "question_text": "What is Python?",
            "correct_answer": "A"
        }
    ]

    result = parse_question_rows(questions)

    assert result[0]["question_id"] == "Q001"


def test_invalid_answer_option():

    questions = [
        {
            "question_id": "Q001",
            "question_text": "What is Python?",
            "correct_answer": "E"
        }
    ]

    with pytest.raises(ValueError):
        parse_question_rows(questions)


def test_missing_question_text():

    questions = [
        {
            "question_id": "Q001",
            "question_text": "",
            "correct_answer": "A"
        }
    ]

    with pytest.raises(ValueError):
        parse_question_rows(questions)


def test_duplicate_question_ids():

    questions = [
        {
            "question_id": "Q001",
            "question_text": "Question one",
            "correct_answer": "A"
        },
        {
            "question_id": "Q001",
            "question_text": "Question two",
            "correct_answer": "B"
        }
    ]

    with pytest.raises(ValueError):
        parse_question_rows(questions)


def test_dynamic_number_of_questions():

    questions = [
        {
            "question_id": f"Q{i:03}",
            "question_text": f"Question {i}",
            "correct_answer": "A"
        }
        for i in range(1, 101)
    ]

    result = parse_question_rows(questions)

    assert len(result) == 100
