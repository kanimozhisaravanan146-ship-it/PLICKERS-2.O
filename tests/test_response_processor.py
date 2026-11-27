"""
Unit tests for RotQR response_processor.py

Run from the project root:

python -m unittest tests.test_response_processor
"""

import unittest
from unittest.mock import patch

from services import response_processor


class TestResponseProcessor(unittest.TestCase):

    def setUp(self):
        """Prepare sample student and question data."""

        self.student = {
            "id": 1,
            "student_name": "Student One",
            "student_token": "ROTQR:test-token-001"
        }

        self.question = {
            "id": 10,
            "question_text": "What is 2 + 2?",
            "correct_answer": "B",
            "is_active": 1
        }

    # --------------------------------------------------
    # TEST 1: VALID RESPONSE
    # --------------------------------------------------

    @patch("services.response_processor.database.save_response")
    @patch("services.response_processor.database.get_student_response")
    @patch("services.response_processor.database.get_active_question")
    @patch("services.response_processor.database.get_student_by_token")
    def test_valid_response_is_recorded(
        self,
        mock_get_student,
        mock_get_question,
        mock_get_previous_response,
        mock_save_response
    ):
        """A valid response should be recorded successfully."""

        mock_get_student.return_value = self.student
        mock_get_question.return_value = self.question

        # First call: student has not answered yet.
        # Second call: response has now been saved.
        mock_get_previous_response.side_effect = [
            None,
            {
                "student_id": 1,
                "question_id": 10,
                "answer": "B",
                "is_correct": 1
            }
        ]

        mock_save_response.return_value = True

        result = response_processor.process_response(
            "ROTQR:test-token-001",
            "B"
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "recorded")
        self.assertEqual(result["answer"], "B")
        self.assertTrue(result["is_correct"])

        mock_save_response.assert_called_once_with(
            1,
            10,
            "B"
        )

    # --------------------------------------------------
    # TEST 2: UNKNOWN STUDENT
    # --------------------------------------------------

    @patch("services.response_processor.database.get_student_by_token")
    def test_unknown_student_is_rejected(
        self,
        mock_get_student
    ):
        """An unregistered QR token should be rejected."""

        mock_get_student.return_value = None

        result = response_processor.process_response(
            "ROTQR:unknown-token",
            "A"
        )

        self.assertFalse(result["success"])
        self.assertEqual(
            result["status"],
            "unknown_student"
        )

    # --------------------------------------------------
    # TEST 3: EMPTY QR TOKEN
    # --------------------------------------------------

    @patch("services.response_processor.database.get_student_by_token")
    def test_empty_token_is_rejected(
        self,
        mock_get_student
    ):
        """An empty QR token should be rejected."""

        result = response_processor.process_response(
            "",
            "A"
        )

        self.assertFalse(result["success"])
        self.assertEqual(
            result["status"],
            "invalid_qr"
        )

        mock_get_student.assert_not_called()

    # --------------------------------------------------
    # TEST 4: INVALID ANSWER
    # --------------------------------------------------

    @patch("services.response_processor.database.get_student_by_token")
    def test_invalid_answer_is_rejected(
        self,
        mock_get_student
    ):
        """An answer other than A, B, C, or D should be rejected."""

        mock_get_student.return_value = self.student

        result = response_processor.process_response(
            "ROTQR:test-token-001",
            "E"
        )

        self.assertFalse(result["success"])
        self.assertEqual(
            result["status"],
            "invalid_answer"
        )

    # --------------------------------------------------
    # TEST 5: NO ACTIVE QUESTION
    # --------------------------------------------------

    @patch("services.response_processor.database.get_student_by_token")
    @patch("services.response_processor.database.get_active_question")
    def test_no_active_question_is_rejected(
        self,
        mock_get_question,
        mock_get_student
    ):
        """A response cannot be saved without an active question."""

        mock_get_student.return_value = self.student
        mock_get_question.return_value = None

        result = response_processor.process_response(
            "ROTQR:test-token-001",
            "A"
        )

        self.assertFalse(result["success"])
        self.assertEqual(
            result["status"],
            "no_active_question"
        )

    # --------------------------------------------------
    # TEST 6: DUPLICATE RESPONSE
    # --------------------------------------------------

    @patch("services.response_processor.database.get_student_by_token")
    @patch("services.response_processor.database.get_active_question")
    @patch("services.response_processor.database.get_student_response")
    def test_duplicate_response_is_rejected(
        self,
        mock_get_previous_response,
        mock_get_question,
        mock_get_student
    ):
        """A student cannot answer the same question twice."""

        mock_get_student.return_value = self.student
        mock_get_question.return_value = self.question

        mock_get_previous_response.return_value = {
            "student_id": 1,
            "question_id": 10,
            "answer": "A",
            "is_correct": 0
        }

        result = response_processor.process_response(
            "ROTQR:test-token-001",
            "B"
        )

        self.assertFalse(result["success"])
        self.assertEqual(
            result["status"],
            "duplicate"
        )

    # --------------------------------------------------
    # TEST 7: DATABASE SAVE FAILURE
    # --------------------------------------------------

    @patch("services.response_processor.database.get_student_by_token")
    @patch("services.response_processor.database.get_active_question")
    @patch("services.response_processor.database.get_student_response")
    @patch("services.response_processor.database.save_response")
    def test_failed_database_save_is_not_counted(
        self,
        mock_save_response,
        mock_get_previous_response,
        mock_get_question,
        mock_get_student
    ):
        """A failed database save must not be reported as recorded."""

        mock_get_student.return_value = self.student
        mock_get_question.return_value = self.question
        mock_get_previous_response.return_value = None

        # Database reports that the response was not saved.
        mock_save_response.return_value = False

        result = response_processor.process_response(
            "ROTQR:test-token-001",
            "B"
        )

        self.assertFalse(result["success"])
        self.assertEqual(
            result["status"],
            "duplicate"
        )


if __name__ == "__main__":
    unittest.main()