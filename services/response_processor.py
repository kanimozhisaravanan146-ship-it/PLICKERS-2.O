"""
RotQR Response Processor

Processes scanned QR tokens and decoded answers.
Checks student identity, active question,
and duplicate submissions.
"""

import database


def process_response(student_token, answer):
    """
    Process one scanned student response.

    Parameters:
        student_token: Unique token decoded from the student's QR.
        answer: Answer decoded from card orientation (A/B/C/D).

    Returns:
        Dictionary containing the response status and message.
    """

    # 1. Validate QR token
    if not student_token or not student_token.strip():
        return {
            "success": False,
            "status": "invalid_qr",
            "message": "QR token is empty."
        }

    student_token = student_token.strip()

    # 2. Validate decoded answer
    if not answer or not answer.strip():
        return {
            "success": False,
            "status": "invalid_answer",
            "message": "Answer could not be decoded."
        }

    answer = answer.strip().upper()

    if answer not in ("A", "B", "C", "D"):
        return {
            "success": False,
            "status": "invalid_answer",
            "message": "Answer must be A, B, C, or D."
        }

    # 3. Find student using the QR token
    student = database.get_student_by_token(student_token)

    if student is None:
        return {
            "success": False,
            "status": "unknown_student",
            "message": "Student QR code is not registered."
        }

    student_id = student["id"]

    # 4. Check whether a question is active
    question = database.get_active_question()

    if question is None:
        return {
            "success": False,
            "status": "no_active_question",
            "message": "There is no active question."
        }

    question_id = question["id"]

    # 5. Prevent duplicate response
    previous_response = database.get_student_response(
        student_id,
        question_id
    )

    if previous_response is not None:
        return {
            "success": False,
            "status": "duplicate",
            "message": "Student has already answered this question.",
            "student_id": student_id,
            "student_name": student["student_name"],
            "question_id": question_id
        }

    # 6. Save response and calculate correctness
    saved = database.save_response(
        student_id,
        question_id,
        answer
    )

    if not saved:
        # Another scan may have saved the answer at the same time.
        return {
            "success": False,
            "status": "duplicate",
            "message": "Response was already recorded.",
            "student_id": student_id,
            "student_name": student["student_name"],
            "question_id": question_id
        }

    # 7. Retrieve the saved response
    response = database.get_student_response(
        student_id,
        question_id
    )

    return {
        "success": True,
        "status": "recorded",
        "message": "Response recorded successfully.",
        "student_id": student_id,
        "student_name": student["student_name"],
        "question_id": question_id,
        "answer": answer,
        "is_correct": bool(response["is_correct"])
    }


def process_multiple_responses(scanned_cards):
    """
    Process multiple cards detected during one camera frame.

    scanned_cards should be a list of dictionaries:
    [
        {"student_token": "ROTQR:token1", "answer": "A"},
        {"student_token": "ROTQR:token2", "answer": "C"}
    ]

    Returns the result for each scanned card.
    """

    results = []

    for card in scanned_cards:

        student_token = card.get("student_token")
        answer = card.get("answer")

        result = process_response(
            student_token,
            answer
        )

        results.append(result)

    return results