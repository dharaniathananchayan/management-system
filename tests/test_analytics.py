import pytest


def test_course_analytics(client, sample_course_hierarchy, test_student):
    course_id = sample_course_hierarchy["course"].course_id
    assessment_id = sample_course_hierarchy["assessment"].assessment_id
    questions = sample_course_hierarchy["questions"]

    # Submit an assessment
    client.post(
        f"/assessments/{assessment_id}/submit",
        json={
            "student_id": test_student.student_id,
            "answers": [
                {"question_id": questions[0].question_id, "answer": "8"},      # correct
                {"question_id": questions[1].question_id, "answer": "wrong"},  # wrong
            ]
        }
    )

    response = client.get(f"/analytics/course/{course_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["course_id"] == course_id
    assert data["total_enrolled"] == 1
    assert data["total_submissions"] == 1
    assert data["average_assessment_score"] == 50.0
    assert "difficult_topics" in data
    assert "grade_distribution" in data
    assert len(data["recommendations"]) >= 1


def test_platform_dashboard_analytics(client, sample_course_hierarchy):
    response = client.get("/analytics/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "total_students" in data
    assert "total_courses" in data
    assert "course_averages" in data
    assert "student_activity_trend" in data


def test_inactive_students_endpoint(client):
    response = client.get("/analytics/inactive-students?days=7")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_low_performing_students_endpoint(client):
    response = client.get("/analytics/low-performers?threshold=60.0")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_analytics_charts_endpoint(client):
    response = client.get("/analytics/charts")
    assert response.status_code == 200
    data = response.json()
    assert "score_bar_chart" in data
    assert "activity_line_chart" in data
    # Validate Plotly dictionary schema
    assert "data" in data["score_bar_chart"]
    assert "layout" in data["score_bar_chart"]
