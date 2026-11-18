import pytest


def test_create_course(client):
    payload = {
        "course_name": "Full Stack FastAPI & React",
        "description": "Modern API development and fullstack systems",
        "status": "Active",
    }
    response = client.post("/courses", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["course_name"] == payload["course_name"]
    assert data["status"] == "Active"
    assert "course_id" in data


def test_list_courses(client, sample_course_hierarchy):
    response = client.get("/courses")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) >= 1
    target = next((c for c in courses if c["course_id"] == sample_course_hierarchy["course"].course_id), None)
    assert target is not None
    assert target["module_count"] == 1
    assert target["student_count"] == 1
    assert target["lesson_count"] == 2


def test_get_course_details(client, sample_course_hierarchy):
    course_id = sample_course_hierarchy["course"].course_id
    response = client.get(f"/courses/{course_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["course_id"] == course_id
    assert len(data["modules"]) == 1
    assert len(data["modules"][0]["lessons"]) == 2


def test_update_course(client, sample_course_hierarchy):
    course_id = sample_course_hierarchy["course"].course_id
    payload = {"course_name": "Advanced Python Automation", "status": "Draft"}
    response = client.put(f"/courses/{course_id}", json=payload)
    assert response.status_code == 200
    assert response.json()["course_name"] == "Advanced Python Automation"
    assert response.json()["status"] == "Draft"


def test_enroll_student_in_course(client, test_student):
    # Create new course
    c_res = client.post("/courses", json={"course_name": "Docker & Kubernetes", "status": "Active"})
    course_id = c_res.json()["course_id"]

    enroll_res = client.post(f"/courses/{course_id}/enroll?student_id={test_student.student_id}")
    assert enroll_res.status_code == 200
    data = enroll_res.json()
    assert data["course_id"] == course_id
    assert data["student_id"] == test_student.student_id
    assert data["status"] == "active"


def test_delete_course(client):
    c_res = client.post("/courses", json={"course_name": "Course To Delete", "status": "Draft"})
    course_id = c_res.json()["course_id"]

    del_res = client.delete(f"/courses/{course_id}")
    assert del_res.status_code == 204

    get_res = client.get(f"/courses/{course_id}")
    assert get_res.status_code == 404
