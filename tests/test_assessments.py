import pytest


def test_create_assessment(client, sample_course_hierarchy):
    course_id = sample_course_hierarchy["course"].course_id
    payload = {
        "course_id": course_id,
        "title": "Module 1 Mastery Quiz",
        "description": "Short checkpoint quiz",
        "total_marks": 50.0,
        "passing_percentage": 70.0,
        "duration_minutes": 10,
    }
    response = client.post("/assessments", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Module 1 Mastery Quiz"
    assert data["total_marks"] == 50.0


def test_get_assessment_hides_correct_answers_for_students(client, sample_course_hierarchy):
    assessment_id = sample_course_hierarchy["assessment"].assessment_id
    response = client.get(f"/assessments/{assessment_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["questions"]) == 2
    # Verify that correct_answer field is omitted from student payload!
    for q in data["questions"]:
        assert "correct_answer" not in q
        assert "question_text" in q
        assert "options" in q


def test_submit_assessment_full_score(client, sample_course_hierarchy, test_student):
    assessment_id = sample_course_hierarchy["assessment"].assessment_id
    questions = sample_course_hierarchy["questions"]

    # Provide correct answers for both questions
    submission_payload = {
        "student_id": test_student.student_id,
        "answers": [
            {"question_id": questions[0].question_id, "answer": "8"},
            {"question_id": questions[1].question_id, "answer": "def"},
        ]
    }
    response = client.post(f"/assessments/{assessment_id}/submit", json=submission_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["percentage"] == 100.0
    assert data["score"] == 100.0
    assert data["passed"] is True
    assert len(data["weak_topics"]) == 0
    assert len(data["recommendations"]) >= 1


def test_submit_assessment_failing_identifies_weak_topics(client, sample_course_hierarchy, test_student):
    assessment_id = sample_course_hierarchy["assessment"].assessment_id
    questions = sample_course_hierarchy["questions"]

    # Provide wrong answers for both questions
    submission_payload = {
        "student_id": test_student.student_id,
        "answers": [
            {"question_id": questions[0].question_id, "answer": "wrong1"},
            {"question_id": questions[1].question_id, "answer": "wrong2"},
        ]
    }
    response = client.post(f"/assessments/{assessment_id}/submit", json=submission_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["percentage"] == 0.0
    assert data["passed"] is False
    # Check that weak topics ("Operators", "Functions") are properly detected!
    assert "Operators" in data["weak_topics"]
    assert "Functions" in data["weak_topics"]
    assert any("Operators" in rec for rec in data["recommendations"])


def test_get_student_results_history(client, sample_course_hierarchy, test_student):
    assessment_id = sample_course_hierarchy["assessment"].assessment_id
    questions = sample_course_hierarchy["questions"]

    # Submit one assessment
    client.post(
        f"/assessments/{assessment_id}/submit",
        json={
            "student_id": test_student.student_id,
            "answers": [{"question_id": questions[0].question_id, "answer": "8"}]
        }
    )

    response = client.get(f"/students/{test_student.student_id}/results")
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert "percentage" in results[0]
    assert "assessment_title" in results[0]
