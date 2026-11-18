import pytest


def test_register_student_success(client):
    payload = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "password": "strongPassword123",
        "role": "student",
    }
    response = client.post("/students/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Jane Doe"
    assert data["email"] == "jane.doe@example.com"
    assert "password_hash" not in data
    assert data["is_active"] is True


def test_register_student_duplicate_email(client, test_student):
    payload = {
        "name": "Duplicate User",
        "email": test_student.email,
        "password": "password123",
    }
    response = client.post("/students/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_student_success(client, test_student):
    payload = {
        "email": test_student.email,
        "password": "password123",
    }
    response = client.post("/students/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["student"]["email"] == test_student.email


def test_login_student_invalid_credentials(client, test_student):
    payload = {
        "email": test_student.email,
        "password": "wrong_password",
    }
    response = client.post("/students/login", json=payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_get_current_student_me(client, auth_headers, test_student):
    response = client.get("/students/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_student.email
    assert data["student_id"] == test_student.student_id


def test_get_student_by_id(client, test_student):
    response = client.get(f"/students/{test_student.student_id}")
    assert response.status_code == 200
    assert response.json()["email"] == test_student.email


def test_update_student_profile(client, test_student):
    payload = {"name": "Updated Name"}
    response = client.put(f"/students/{test_student.student_id}", json=payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"
