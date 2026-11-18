import pytest


def test_mark_lesson_completed(client, sample_course_hierarchy, test_student):
    lesson_id = sample_course_hierarchy["lessons"][0].lesson_id
    payload = {"student_id": test_student.student_id, "status": "completed"}
    response = client.post(f"/progress/lessons/{lesson_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["lesson_id"] == lesson_id
    assert data["status"] == "completed"
    assert data["completed_at"] is not None


def test_student_progress_summary(client, sample_course_hierarchy, test_student):
    lessons = sample_course_hierarchy["lessons"]
    # Mark first lesson completed
    client.post(
        f"/progress/lessons/{lessons[0].lesson_id}",
        json={"student_id": test_student.student_id, "status": "completed"}
    )

    response = client.get(f"/students/{test_student.student_id}/progress")
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == test_student.student_id
    assert data["enrolled_courses_count"] == 1
    assert data["completed_lessons_count"] == 1
    assert len(data["course_progress"]) == 1
    # 1 of 2 lessons completed = 50%
    assert data["course_progress"][0]["completion_percentage"] == 50.0


def test_student_progress_list(client, sample_course_hierarchy, test_student):
    lessons = sample_course_hierarchy["lessons"]
    client.post(
        f"/progress/lessons/{lessons[0].lesson_id}",
        json={"student_id": test_student.student_id, "status": "completed"}
    )
    response = client.get(f"/progress/student/{test_student.student_id}")
    assert response.status_code == 200
    records = response.json()
    assert len(records) >= 1
    assert records[0]["status"] == "completed"
