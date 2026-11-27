"""
RotQR Result Service

Prepares question results and student-wise
response information for the dashboard.
"""

import database


def get_active_results():
    """
    Get summary results for the active question.

    Returns total students, submitted responses,
    correct answers, incorrect answers,
    and students who have not answered.
    """

    summary = database.get_active_question_results()

    if summary is None:
        return {
            "success": False,
            "message": "No active question.",
            "results": None
        }

    total_students = summary["total_students"]
    submitted = summary["submitted"]
    correct = summary["correct"]
    incorrect = summary["incorrect"]

    unanswered = total_students - submitted

    if total_students > 0:
        response_percentage = round(
            (submitted / total_students) * 100, 2
        )
    else:
        response_percentage = 0

    return {
        "success": True,
        "message": "Results retrieved successfully.",
        "results": {
            "question": summary["question"],
            "total_students": total_students,
            "submitted": submitted,
            "unanswered": unanswered,
            "correct": correct,
            "incorrect": incorrect,
            "response_percentage": response_percentage
        }
    }


def get_student_wise_results(question_id):
    """
    Get the answer submitted by each student
    for a particular question.
    """

    question = database.get_question_by_id(question_id)

    if question is None:
        raise ValueError("Question not found.")

    students = database.get_students()

    responses = database.get_question_results(question_id)

    # Create a lookup dictionary using student ID.
    response_lookup = {
        response["student_id"]: response
        for response in responses
    }

    student_results = []

    for student in students:

        response = response_lookup.get(student["id"])

        if response is None:
            student_results.append({
                "student_id": student["id"],
                "student_name": student["student_name"],
                "answer": None,
                "status": "unanswered",
                "is_correct": None
            })

        else:
            student_results.append({
                "student_id": student["id"],
                "student_name": student["student_name"],
                "answer": response["answer"],
                "status": "answered",
                "is_correct": bool(response["is_correct"])
            })

    return student_results


def get_question_summary(question_id):
    """
    Get summary statistics for a specific question.
    """

    question = database.get_question_by_id(question_id)

    if question is None:
        raise ValueError("Question not found.")

    students = database.get_students()

    responses = database.get_question_results(question_id)

    total_students = len(students)
    submitted = len(responses)

    correct = sum(
        1 for response in responses
        if response["is_correct"] == 1
    )

    incorrect = submitted - correct
    unanswered = total_students - submitted

    return {
        "question_id": question_id,
        "question_text": question["question_text"],
        "total_students": total_students,
        "submitted": submitted,
        "unanswered": unanswered,
        "correct": correct,
        "incorrect": incorrect
    }


def get_results_for_dashboard():
    """
    Get all information needed by the dashboard
    for the currently active question.
    """

    summary = get_active_results()

    if not summary["success"]:
        return summary

    question = summary["results"]["question"]

    question_id = question["id"]

    student_results = get_student_wise_results(
        question_id
    )

    return {
        "success": True,
        "question": question,
        "summary": summary["results"],
        "students": student_results
    }