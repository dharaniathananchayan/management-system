import pytest


def test_create_enrollment_with_form_fields(client, test_student, sample_course_hierarchy):
    course_id = sample_course_hierarchy["course"].course_id
    
    # Create another course to avoid unique constraint with sample fixture
    c_res = client.post("/courses", json={"course_name": "Cloud Architecture", "status": "Active"})
    new_course_id = c_res.json()["course_id"]

    # Form payload using enrollment_id, student_id, and course_id
    payload = {
        "enrollment_id": 999,
        "student_id": test_student.student_id,
        "course_id": new_course_id,
        "status": "active",
    }
    response = client.post("/enrollments", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["enrollment_id"] == 999
    assert data["student_id"] == test_student.student_id
    assert data["course_id"] == new_course_id
    assert data["student_name"] == test_student.name
    assert data["status"] == "active"


def test_create_enrollment_auto_generated_id(client, test_student):
    c_res = client.post("/courses", json={"course_name": "Machine Learning Fundamentals", "status": "Active"})
    new_course_id = c_res.json()["course_id"]

    payload = {
        "student_id": test_student.student_id,
        "course_id": new_course_id,
    }
    response = client.post("/enrollments", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "enrollment_id" in data
    assert data["student_id"] == test_student.student_id
    assert data["course_id"] == new_course_id


def test_create_enrollment_duplicate_fails(client, test_student, sample_course_hierarchy):
    # Already enrolled in sample fixture
    course_id = sample_course_hierarchy["course"].course_id
    payload = {
        "student_id": test_student.student_id,
        "course_id": course_id,
    }
    response = client.post("/enrollments", json=payload)
    assert response.status_code == 400
    assert "already enrolled" in response.json()["detail"].lower()


def test_list_and_delete_enrollment(client, sample_course_hierarchy, test_student):
    # List enrollments (sample_course_hierarchy already enrolls test_student)
    response = client.get("/enrollments")
    assert response.status_code == 200
    enrollments = response.json()
    assert len(enrollments) >= 1

    first_id = enrollments[0]["enrollment_id"]
    get_res = client.get(f"/enrollments/{first_id}")
    assert get_res.status_code == 200
    assert get_res.json()["enrollment_id"] == first_id

    # Delete/drop enrollment
    del_res = client.delete(f"/enrollments/{first_id}")
    assert del_res.status_code == 204

    # Verify 404 after deletion
    get_after = client.get(f"/enrollments/{first_id}")
    assert get_after.status_code == 404
