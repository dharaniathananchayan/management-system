import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.security import hash_password, create_access_token
from app.models.student import Student
from app.models.course import Course, Module, Lesson
from app.models.enrollment import Enrollment
from app.models.assessment import Assessment, Question, Result, StudentAnswer
from app.models.progress import Progress

# Isolated in-memory SQLite database for test suite
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_student(db_session):
    student = Student(
        name="Test Student",
        email="test.student@example.com",
        password_hash=hash_password("password123"),
        role="student",
        is_active=True,
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


@pytest.fixture
def auth_headers(test_student):
    token = create_access_token(data={"sub": str(test_student.student_id), "email": test_student.email, "role": "student"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_course_hierarchy(db_session, test_student):
    course = Course(course_name="Python Automation", description="Learn backend automation", status="Active")
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)

    module = Module(course_id=course.course_id, module_name="Module 1: Basics", order_index=1)
    db_session.add(module)
    db_session.commit()
    db_session.refresh(module)

    lesson1 = Lesson(module_id=module.module_id, lesson_title="Lesson 1: Intro", content="Intro content", duration_minutes=15, order_index=1)
    lesson2 = Lesson(module_id=module.module_id, lesson_title="Lesson 2: Advanced", content="Advanced content", duration_minutes=25, order_index=2)
    db_session.add_all([lesson1, lesson2])
    db_session.commit()

    # Enroll student
    enrollment = Enrollment(student_id=test_student.student_id, course_id=course.course_id, status="active")
    db_session.add(enrollment)
    db_session.commit()

    # Create assessment
    assessment = Assessment(
        course_id=course.course_id,
        title="Python Basics Quiz",
        description="Test basic knowledge",
        total_marks=100.0,
        passing_percentage=60.0,
        duration_minutes=15,
    )
    db_session.add(assessment)
    db_session.commit()
    db_session.refresh(assessment)

    q1 = Question(
        module_id=module.module_id,
        assessment_id=assessment.assessment_id,
        question_text="What is the output of print(2 ** 3)?",
        question_type="multiple_choice",
        correct_answer="8",
        points=50.0,
        topic="Operators",
    )
    q1.options = ["6", "8", "9", "Error"]

    q2 = Question(
        module_id=module.module_id,
        assessment_id=assessment.assessment_id,
        question_text="Which keyword defines a function?",
        question_type="multiple_choice",
        correct_answer="def",
        points=50.0,
        topic="Functions",
    )
    q2.options = ["func", "def", "function", "lambda"]

    db_session.add_all([q1, q2])
    db_session.commit()

    return {
        "course": course,
        "module": module,
        "lessons": [lesson1, lesson2],
        "assessment": assessment,
        "questions": [q1, q2],
    }
