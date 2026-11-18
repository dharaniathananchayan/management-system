# ArchintX — Learning Progress & Assessment Management System
**Advanced Python Development Project Assignment | ArchintX Python Development Team**

A production-grade Python backend system built with **FastAPI**, **SQLAlchemy**, **Pydantic**, **Pandas**, and **Plotly** to manage student learning activities, assessments, automated quiz grading, progress tracking, and performance analytics.

---

## 🌟 Key Features & Deliverables

- **Student Management Module**:
  - Secure registration & login with **bcrypt** password hashing and **JWT** (JSON Web Token) authentication.
  - Student profile updates, enrollments, and permission scopes.
- **Course & Module Management**:
  - Full CRUD operations for courses, modules, and lessons.
  - Course status workflow (`Active`, `Draft`, `Archived`).
  - Student enrollment tracking and module lesson counts.
- **Quiz & Assessment Engine**:
  - Multiple-choice and modular question types.
  - Timed quizzes with duration countdown.
  - Automated question evaluation with instant score calculation, percentage grading, and pass/fail determination.
  - Automatic weak-topic detection and personalized learning recommendations.
- **Learning Progress Tracking**:
  - Granular lesson-by-lesson completion logging (`completed` vs. `pending`).
  - Course completion percentage calculations.
  - Inactive student detection (flagging accounts with no progress in > 7 days).
- **Performance Analytics**:
  - **Pandas**-powered analytics for grade distribution, pass rates, and course averages.
  - **Plotly** interactive data visualization endpoints (Bar charts for course averages and line charts for activity trends).
  - Identification of difficult topics based on accuracy percentages.
- **Interactive UI Dashboard**:
  - Fully functional web interface served at `/` implementing all 4 mockups from the assignment specification (Student Dashboard, Course Management, Quiz Assessment, Learning Analytics).
- **Complete Test Suite**:
  - Comprehensive **Pytest** automated testing suite with 26 unit and integration test cases covering 100% of core flows.

---

## 🏗️ System Architecture & Technology Stack

```
                          ┌────────────────────────┐
                          │   Frontend / Client    │
                          │   (Web Dashboard &     │
                          │   Swagger / ReDoc UI)  │
                          └───────────┬────────────┘
                                      │ HTTP / REST
                                      ▼
                          ┌────────────────────────┐
                          │    FastAPI Gateway     │
                          │   (Pydantic Validation,│
                          │   CORS, JWT Security)  │
                          └───────────┬────────────┘
                                      │
         ┌───────────────┬────────────┼───────────────┬────────────────┐
         ▼               ▼            ▼               ▼                ▼
   ┌───────────┐   ┌───────────┐ ┌─────────┐   ┌─────────────┐  ┌─────────────┐
   │Auth Module│   │Course CRUD│ │Quiz Eng.│   │Progress Svc │  │Analytics Svc│
   │  (JWT /   │   │  & Lessons│ │(Auto-   │   │(Completion  │  │ (Pandas &   │
   │  Bcrypt)  │   │           │ │ Grading)│   │ Monitoring) │  │   Plotly)   │
   └─────┬─────┘   └─────┬─────┘ └────┬────┘   └──────┬──────┘  └──────┬──────┘
         │               │            │               │                │
         └───────────────┴────────────┼───────────────┴────────────────┘
                                      ▼
                          ┌────────────────────────┐
                          │    SQLAlchemy ORM      │
                          │  (Session Management)  │
                          └───────────┬────────────┘
                                      ▼
                          ┌────────────────────────┐
                          │   Relational Database  │
                          │  (SQLite / PostgreSQL /│
                          │        MySQL)          │
                          └────────────────────────┘
```

| Technology | Purpose |
|---|---|
| **Python 3.10+** | Core programming language & async runtime |
| **FastAPI** | High-performance async REST API framework |
| **SQLAlchemy 2.0** | Relational Database ORM and schema modeling |
| **Pydantic v2** | Request validation, schema enforcement, and serialization |
| **JWT (PyJWT)** | Stateless bearer token authentication |
| **Bcrypt** | Industry-standard salt-hashed password storage |
| **Pandas** | Tabular data analysis and aggregations |
| **Plotly** | Dynamic chart JSON generation for analytics visualizations |
| **Pytest** | Automated test suite with isolated test fixtures |
| **Swagger / OpenAPI** | Interactive API documentation |

---

## 🗄️ Database Design (Entity-Relationship)

```mermaid
erDiagram
    STUDENTS ||--o{ ENROLLMENTS : registers
    COURSES ||--o{ ENROLLMENTS : contains
    COURSES ||--o{ MODULES : organizes
    MODULES ||--o{ LESSONS : contains
    MODULES ||--o{ QUESTIONS : pools
    COURSES ||--o{ ASSESSMENTS : includes
    ASSESSMENTS ||--o{ QUESTIONS : contains
    ASSESSMENTS ||--o{ RESULTS : evaluates
    STUDENTS ||--o{ RESULTS : receives
    STUDENTS ||--o{ STUDENT_ANSWERS : submits
    QUESTIONS ||--o{ STUDENT_ANSWERS : answered_by
    STUDENTS ||--o{ PROGRESS : tracks
    LESSONS ||--o{ PROGRESS : logged_in

    STUDENTS {
        int student_id PK
        string name
        string email UK
        string password_hash
        string role
        boolean is_active
        datetime created_at
    }

    COURSES {
        int course_id PK
        string course_name
        text description
        string status
        datetime created_at
    }

    MODULES {
        int module_id PK
        int course_id FK
        string module_name
        int order_index
    }

    LESSONS {
        int lesson_id PK
        int module_id FK
        string lesson_title
        text content
        int duration_minutes
        int order_index
    }

    ENROLLMENTS {
        int enrollment_id PK
        int student_id FK
        int course_id FK
        datetime enrolled_at
        string status
    }

    ASSESSMENTS {
        int assessment_id PK
        int course_id FK
        string title
        float total_marks
        float passing_percentage
        int duration_minutes
    }

    QUESTIONS {
        int question_id PK
        int module_id FK
        int assessment_id FK
        text question_text
        string question_type
        text options_json
        string correct_answer
        float points
        string topic
    }

    STUDENT_ANSWERS {
        int answer_id PK
        int student_id FK
        int assessment_id FK
        int question_id FK
        text answer
        boolean is_correct
        float marks_awarded
        datetime submitted_at
    }

    RESULTS {
        int result_id PK
        int student_id FK
        int assessment_id FK
        float score
        float percentage
        boolean passed
        text feedback
        datetime completed_at
    }

    PROGRESS {
        int progress_id PK
        int student_id FK
        int lesson_id FK
        string status
        datetime completed_at
        datetime updated_at
    }
```

---

## 🚀 Quickstart Guide

### 1. Clone & Set Up Environment

```bash
# Clone the repository
git clone <repository_url>
cd management-system

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
By default, the application runs on SQLite (`sqlite:///./archintx.db`) with zero external dependencies required. To run with PostgreSQL or MySQL, update `DATABASE_URL` in `.env`:
- **PostgreSQL**: `DATABASE_URL=postgresql://user:password@localhost:5432/archintx`
- **MySQL**: `DATABASE_URL=mysql+pymysql://user:password@localhost:3306/archintx`

### 3. Seed Database with Realistic Data

```bash
python database/seed_data.py
```
This populates:
- 4 student profiles & 1 instructor profile
- 4 complete courses matching the specification:
  - *Python Fundamentals* (8 modules)
  - *SQL for Beginners* (6 modules)
  - *API Development* (5 modules)
  - *Data Analytics* (7 modules)
- Lesson progress records calibrated to replicate the exact metrics of the assignment mockups
- Quizzes with 10 multiple-choice questions and assessment historical results

### 4. Run the Application

```bash
python run.py
```
The server will start on `http://127.0.0.1:8000`.

- **Interactive Dashboard (All 4 Mockups)**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 Automated Testing

Execute the test suite with verbose output:

```bash
pytest -v
```

All **26 tests** will pass:
```text
tests/test_analytics.py::test_course_analytics PASSED
tests/test_analytics.py::test_platform_dashboard_analytics PASSED
tests/test_analytics.py::test_inactive_students_endpoint PASSED
tests/test_analytics.py::test_low_performing_students_endpoint PASSED
tests/test_analytics.py::test_analytics_charts_endpoint PASSED
tests/test_assessments.py::test_create_assessment PASSED
tests/test_assessments.py::test_get_assessment_hides_correct_answers_for_students PASSED
tests/test_assessments.py::test_submit_assessment_full_score PASSED
tests/test_assessments.py::test_submit_assessment_failing_identifies_weak_topics PASSED
tests/test_assessments.py::test_get_student_results_history PASSED
tests/test_auth.py::test_register_student_success PASSED
tests/test_auth.py::test_register_student_duplicate_email PASSED
tests/test_auth.py::test_login_student_success PASSED
tests/test_auth.py::test_login_student_invalid_credentials PASSED
tests/test_auth.py::test_get_current_student_me PASSED
tests/test_auth.py::test_get_student_by_id PASSED
tests/test_auth.py::test_update_student_profile PASSED
tests/test_courses.py::test_create_course PASSED
tests/test_courses.py::test_list_courses PASSED
tests/test_courses.py::test_get_course_details PASSED
tests/test_courses.py::test_update_course PASSED
tests/test_courses.py::test_enroll_student_in_course PASSED
tests/test_courses.py::test_delete_course PASSED
tests/test_progress.py::test_mark_lesson_completed PASSED
tests/test_progress.py::test_student_progress_summary PASSED
tests/test_progress.py::test_student_progress_list PASSED

====================== 26 passed in 9.20s =======================
```

---

## 📡 REST API Specification

### Student Management
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/students/register` | Register new student with bcrypt hashing |
| `POST` | `/students/login` | Authenticate student and obtain JWT Bearer token |
| `GET` | `/students/me` | Fetch currently authenticated student profile |
| `GET` | `/students` | List students (supports pagination & role filter) |
| `GET` | `/students/{id}` | Get student details |
| `PUT` | `/students/{id}` | Update student profile |
| `GET` | `/students/{id}/results` | Get assessment history and answer breakdown |
| `GET` | `/students/{id}/progress` | Get student progress report (matching Mockup 1) |

### Course Management
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/courses` | Create new course |
| `GET` | `/courses` | List courses with module/student counts (Mockup 2) |
| `GET` | `/courses/{id}` | Get course detail hierarchy (modules & lessons) |
| `PUT` | `/courses/{id}` | Update course title/status/description |
| `DELETE` | `/courses/{id}` | Delete course (cascades modules & lessons) |
| `POST` | `/courses/{id}/enroll` | Enroll a student in a course |
| `POST` | `/courses/{id}/modules` | Add module to course |
| `GET` | `/courses/{id}/modules` | List modules for course |
| `POST` | `/modules/{id}/lessons` | Add lesson to module |
| `GET` | `/lessons/{id}` | Get lesson details |

### Quiz & Assessment Module
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/assessments` | Create assessment quiz |
| `GET` | `/assessments` | List assessments |
| `GET` | `/assessments/{id}` | Get assessment questions (hides answer for students) |
| `POST` | `/assessments/{id}/questions` | Add question to assessment |
| `POST` | `/assessments/{id}/submit` | Submit answers for automatic evaluation & scoring |

### Progress Tracking & Analytics
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/progress/lessons/{id}` | Update lesson progress (`completed`/`pending`) |
| `GET` | `/progress/student/{id}` | Get student lesson progress list |
| `GET` | `/analytics/course/{id}` | Course-level analytics with Pandas |
| `GET` | `/analytics/dashboard` | Platform metrics & student activity trend |
| `GET` | `/analytics/inactive-students`| List students with no activity in > 7 days |
| `GET` | `/analytics/low-performers` | Identify students with scores below threshold |
| `GET` | `/analytics/charts` | Plotly chart JSON definitions (Mockup 4) |

---

## 🎨 UI Mockups Implementation Mapping

The interactive frontend served at root (`/`) maps directly to the design mockups in the specification:

1. **Example 1 — Student Dashboard**:
   - Welcome message: *"Welcome back, Student"*
   - 3 metric cards: **Enrolled Courses (4)**, **Completed Lessons (18)**, **Average Score (82%)**
   - Course progress percentage bars for *Python Fundamentals (78%)*, *SQL Basics (55%)*, and *Web Development (32%)*.
2. **Example 2 — Course Management**:
   - Courses table showing **Course Name**, **Modules**, **Students Enrolled**, and **Status Badge** (*Active*, *Draft*).
   - Dynamic modal for creating new courses.
3. **Example 3 — Quiz Assessment**:
   - Quiz assessment header: *"ArchintX | Python Assessment"*
   - Live timer countdown (`Time left: 12:45`) and progress indicator (`Question 3 of 10`).
   - Multiple-choice layout: Question text with option cards (e.g. *A. 6, B. 8, C. 9, D. Error*).
   - Automated submission and grading with instant feedback.
4. **Example 4 — Learning Analytics**:
   - **Average assessment score by course** bar chart (*Python: 72%, SQL: 84%, Web: 68%, Data: 91%*).
   - **Student activity trend** spline line chart (*Mon - Sat*).
   - Weak topics breakdown and inactive students alert panel.

---

## 🔒 Security & Best Practices

- **Zero Plain-Text Passwords**: Passwords hashed using `bcrypt` with adaptive salt cost factor.
- **Strict JWT Token Verification**: Cryptographic HS256 validation with expiration window.
- **SQL Injection Prevention**: Completely mitigated through parameterized queries via SQLAlchemy ORM.
- **Input Validation**: Robust Pydantic v2 schemas validating request structures, data types, and bounds.
- **Graceful Error Handling**: Global exception handler with clean JSON error details.
