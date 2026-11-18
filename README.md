# Learning Progress & Assessment Management System

A production-grade Python full-stack application built with **FastAPI**, **SQLAlchemy**, **Pydantic v2**, **Pandas**, **Plotly**, and **Tailwind CSS**. The platform provides complete student lifecycle management, course curriculum authoring, automated quiz grading, granular lesson progress tracking, and academic performance analytics.

---

## 📑 Table of Contents
- [Core Architecture & Capabilities](#-core-architecture--capabilities)
- [System Architecture](#-system-architecture)
- [Database Schema & ER Diagram](#-database-schema--er-diagram)
- [Core Modules Breakdown (Tasks A–F)](#-core-modules-breakdown-tasks-af)
- [Interactive UI Dashboard](#-interactive-ui-dashboard)
- [REST API Specification](#-rest-api-specification)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation & Setup](#installation--setup)
  - [Database Seeding](#database-seeding)
  - [Running the Server](#running-the-server)
- [Automated Testing Suite](#-automated-testing-suite)
- [Project Directory Structure](#-project-directory-structure)
- [Security & Engineering Best Practices](#-security--engineering-best-practices)

---

## 🌟 Core Architecture & Capabilities

- **Python 3.10+ & FastAPI**: High-throughput asynchronous backend with automatic OpenAPI documentation.
- **Relational ORM**: SQLAlchemy 2.0 with native support for SQLite, PostgreSQL, and MySQL.
- **JWT & Cryptographic Security**: Industry-standard `bcrypt` password hashing and stateless HS256 JWT authentication.
- **Automated Assessment Engine**: Real-time evaluation of student quiz submissions, score calculation, pass/fail grading, and weak topic identification.
- **Pandas & Plotly Analytics**: Statistical data transformations, course difficulty evaluations, and interactive analytical visualisations.
- **Modern Responsive UI**: Clean single-page dashboard with dedicated modals for authentication, course authoring, quiz taking, curriculum inspection, and progress reporting.

---

## 🏗️ System Architecture

```
                          ┌────────────────────────┐
                          │     Web Dashboard      │
                          │ (HTML5 / Tailwind CSS /│
                          │   Plotly Analytics)    │
                          └───────────┬────────────┘
                                      │ HTTP / JSON REST
                                      ▼
                          ┌────────────────────────┐
                          │    FastAPI Gateway     │
                          │  (Pydantic Validation, │
                          │   CORS, JWT Security)  │
                          └───────────┬────────────┘
                                      │
         ┌───────────────┬────────────┼───────────────┬────────────────┐
         ▼               ▼            ▼               ▼                ▼
   ┌───────────┐   ┌───────────┐ ┌─────────┐   ┌─────────────┐  ┌─────────────┐
   │Student Mgt│   │Course CRUD│ │Quiz Eng.│   │Progress Svc │  │Analytics Svc│
   │ (Auth/JWT/│   │& Learning │ │ (Auto-  │   │ (Completion │  │  (Pandas &  │
   │ Profiles) │   │ Materials)│ │ Grading)│   │ Monitoring) │  │   Plotly)   │
   └─────┬─────┘   └─────┬─────┘ └────┬────┘   └──────┬──────┘  └──────┬──────┘
         │               │            │               │                │
         └───────────────┴────────────┼───────────────┴────────────────┘
                                      ▼
                          ┌────────────────────────┐
                          │    SQLAlchemy 2.0      │
                          │  (Session Management)  │
                          └───────────┬────────────┘
                                      ▼
                          ┌────────────────────────┐
                          │  Relational Database   │
                          │ (SQLite/Postgres/MySQL)│
                          └────────────────────────┘
```

---

## 🗄️ Database Schema & ER Diagram

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
        string level
        int duration_hours
        int passing_criteria
        string instructor_name
        string prerequisites
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

## 🧩 Core Modules Breakdown (Tasks A–F)

### A. Student Management Module
- **Registration & Login**: Secure endpoints with bcrypt password hashing and JWT token issuance.
- **Profile Management**: Profile retrieval and profile editing (`PUT /students/{id}`).
- **Course Enrollment**: Enroll students into courses with status tracking (`Active`, `Completed`, `Dropped`).
- **Interactive UI**:
  - Modal for registering new students with automatic persona activation.
  - Dedicated Sign In modal issuing JWT bearer tokens.
  - Interactive profile editing modal and student switcher.

### B. Course Management Module
- **Curriculum Hierarchy**: Courses contain Modules, which contain Lessons and learning materials.
- **CRUD Operations**: Create, update, list, and delete courses, modules, and lessons.
- **Uniform Status Workflow**: Clean course statuses (`Active`, `Draft`, `Archived`) with uniform card presentation.
- **Interactive UI**:
  - Modal for authoring courses with duration, level, passing criteria, and prerequisites.
  - Curriculum inspection modal allowing lesson completion toggles and module additions.
  - Modal for enrolling learners into existing courses.

### C. Quiz & Assessment Module
- **Question Engine**: Support for multiple-choice questions (MCQs) and modular question types.
- **Automated Grading**: Automatic evaluation comparing student answers against answer keys.
- **Results & History**: Automatic calculation of marks, percentage score, pass/fail status, and weak topic diagnostics.
- **Interactive UI**:
  - Live quiz-taking modal with countdown timer, dynamic progress tracking, and clean radio selectors.
  - Instant score feedback modal displaying percentage, status, and targeted recommendations.
  - Modal for creating new assessments and adding questions.

### D. Learning Progress Tracking
- **Granular Lesson Tracking**: Per-lesson status tracking (`completed` vs. `pending`).
- **Dynamic Completion Calculations**: Instant calculation of course progress percentages across all enrolled modules.
- **Inactive Student Detection**: Automated detection of learners with no activity in over 7 days.
- **Interactive UI**:
  - Full-featured Student Progress Report modal with printable transcript view (`window.print()`).
  - Visual completion progress bars across all courses.
  - Inactive student alert cards with one-click study nudge action.

### E. Performance Analytics
- **At-Risk Learner Identification**: Automated identification of students with average assessment scores below threshold (default: 60%).
- **Course Performance Averages**: Aggregation of student scores across all courses using Pandas.
- **Difficult Topic Discovery**: Topic-level accuracy rate analysis to pinpoint challenging curriculum concepts.
- **Interactive UI**:
  - Low-Performing Students table displaying score metrics, completed tests, and intervention actions.
  - Plotly bar chart displaying average scores by course.
  - Plotly spline line chart illustrating 7-day student activity trends.
  - Difficult topics breakdown list with accuracy progress bars.

### F. API Integration & Architecture
- **FastAPI Framework**: High performance async REST APIs with Pydantic v2 data validation.
- **Error Handling**: Standardized HTTP exceptions and formatted error messages.
- **Pagination & Filtering**: Query parameters for filtering students, enrollments, and courses.
- **Auto-Generated Documentation**: Complete OpenAPI 3.0 schema accessible via `/docs` and `/redoc`.

---

## 🎨 Interactive UI Dashboard

The platform includes a modern web dashboard served directly at `/`:

1. **Top Navigation Bar**:
   - Header identity: `Learning Progress & Assessment Management`
   - Active student switcher with live profile data binding.
   - Quick access buttons: **Sign In** (JWT Authentication) and **+ New Student** (Registration).
2. **Student Dashboard Tab**:
   - Summary metric cards: Enrolled Courses, Completed Lessons, and Overall Average Score.
   - Course progress cards with visual percentage bars.
   - Profile action buttons: **Edit Profile** and **Progress Report**.
3. **Course Catalog Tab**:
   - Status filters: `All`, `Active`, `Draft`, `Archived`.
   - Course cards displaying duration, difficulty level, module count, and enrolled student count.
   - Action buttons: **Curriculum** (view/manage lessons) and **Enroll Student**.
   - **+ New Course** creation button with modal workflow.
4. **Quiz & Assessment Tab**:
   - Available assessments list with duration, total marks, and passing percentage.
   - **Take Assessment** interactive modal with real-time countdown timer.
   - Assessment creation modal to author custom quizzes.
   - Assessment history table showing past attempts and scores.
5. **Analytics & Performance Tab**:
   - Key platform metrics (Active Students, Total Enrollments, Platform Avg Score, Assessments Taken).
   - Interactive Plotly visualizations (Course Score Averages & Weekly Activity Trend).
   - Inactive students re-engagement list.
   - Low-performing students intervention table.
   - Course-specific difficult topics breakdown.

---

## 📡 REST API Specification

### Student Management
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/students/register` | Register new student profile with bcrypt password hashing |
| `POST` | `/students/login` | Authenticate student credentials and issue JWT bearer token |
| `GET` | `/students/me` | Retrieve currently authenticated student profile via JWT |
| `GET` | `/students` | List students with optional role filter and pagination |
| `GET` | `/students/{id}` | Get individual student profile |
| `PUT` | `/students/{id}` | Update student name, email, or role |
| `GET` | `/students/{id}/results` | Get assessment history and answer breakdown for student |
| `GET` | `/students/{id}/progress` | Get comprehensive student progress transcript |

### Course & Curriculum Management
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/courses` | Create new course with curriculum metadata |
| `GET` | `/courses` | List courses with enrolled student counts and module counts |
| `GET` | `/courses/{id}` | Get course detail hierarchy including modules and lessons |
| `PUT` | `/courses/{id}` | Update course title, level, status, or description |
| `DELETE` | `/courses/{id}` | Delete course (cascades modules and lessons) |
| `POST` | `/courses/{id}/enroll` | Enroll a student into a course |
| `POST` | `/courses/{id}/modules` | Add a curriculum module to a course |
| `GET` | `/courses/{id}/modules` | List modules belonging to a course |
| `POST` | `/modules/{id}/lessons` | Add a lesson to a module |
| `GET` | `/lessons/{id}` | Get lesson details and content |

### Quiz & Assessment Module
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/assessments` | Create assessment quiz with time limits and passing criteria |
| `GET` | `/assessments` | List all available assessments |
| `GET` | `/assessments/{id}` | Get assessment questions (omits correct answers for test-takers) |
| `POST` | `/assessments/{id}/questions` | Add a question to an assessment |
| `POST` | `/assessments/{id}/submit` | Submit student answers for automated evaluation and scoring |

### Progress Tracking & Performance Analytics
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/progress/lessons/{id}` | Update lesson completion status (`completed` or `pending`) |
| `GET` | `/progress/student/{id}` | Get student lesson progress records |
| `GET` | `/analytics/course/{id}` | Course-level statistical analysis via Pandas |
| `GET` | `/analytics/dashboard` | Overall platform KPIs and activity trends |
| `GET` | `/analytics/inactive-students`| List students with no recorded activity in > 7 days |
| `GET` | `/analytics/low-performers` | Identify learners with average scores below passing threshold |
| `GET` | `/analytics/charts` | Plotly JSON chart configurations for dashboard rendering |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14
- Git

### Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd management-system
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows (PowerShell):
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS:
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables** (Optional):
   ```bash
   cp .env.example .env
   ```
   *Default database is SQLite (`sqlite:///./lms.db`). To switch to PostgreSQL or MySQL, update `DATABASE_URL` in `.env`:*
   - **PostgreSQL**: `DATABASE_URL=postgresql://user:password@localhost:5432/lms`
   - **MySQL**: `DATABASE_URL=mysql+pymysql://user:password@localhost:3306/lms`

### Database Seeding

Populate the database with realistic courses, curriculum modules, lessons, student profiles, assessments, and progress records:

```bash
python database/seed_data.py
```

### Running the Server

Start the application with Uvicorn:

```bash
python run.py
```

- **Interactive UI Dashboard**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Swagger API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 Automated Testing Suite

The project includes 32 automated tests covering authentication, course management, assessment grading, progress calculation, and analytics logic.

Run the test suite with verbose output:

```bash
pytest -v
```

### Test Suite Summary:
```text
tests/test_analytics.py::test_course_analytics PASSED                    [  3%]
tests/test_analytics.py::test_platform_dashboard_analytics PASSED        [  6%]
tests/test_analytics.py::test_inactive_students_endpoint PASSED          [  9%]
tests/test_analytics.py::test_low_performing_students_endpoint PASSED    [ 12%]
tests/test_analytics.py::test_analytics_charts_endpoint PASSED           [ 15%]
tests/test_assessments.py::test_create_assessment PASSED                 [ 18%]
tests/test_assessments.py::test_get_assessment_hides_correct_answers_for_students PASSED [ 21%]
tests/test_assessments.py::test_submit_assessment_full_score PASSED      [ 25%]
tests/test_assessments.py::test_submit_assessment_failing_identifies_weak_topics PASSED [ 28%]
tests/test_assessments.py::test_get_student_results_history PASSED       [ 31%]
tests/test_auth.py::test_register_student_success PASSED                 [ 34%]
tests/test_auth.py::test_register_student_duplicate_email PASSED         [ 37%]
tests/test_auth.py::test_login_student_success PASSED                    [ 40%]
tests/test_auth.py::test_login_student_invalid_credentials PASSED        [ 43%]
tests/test_auth.py::test_get_current_student_me PASSED                   [ 46%]
tests/test_auth.py::test_get_student_by_id PASSED                        [ 50%]
tests/test_auth.py::test_update_student_profile PASSED                   [ 53%]
tests/test_courses.py::test_create_course PASSED                         [ 56%]
tests/test_courses.py::test_list_courses PASSED                          [ 59%]
tests/test_courses.py::test_get_course_details PASSED                    [ 62%]
tests/test_courses.py::test_update_course PASSED                         [ 65%]
tests/test_courses.py::test_enroll_student_in_course PASSED              [ 68%]
tests/test_courses.py::test_delete_course PASSED                         [ 71%]
tests/test_enrollments.py::test_create_enrollment_with_form_fields PASSED [ 75%]
tests/test_enrollments.py::test_create_enrollment_auto_generated_id PASSED [ 78%]
tests/test_enrollments.py::test_create_enrollment_duplicate_fails PASSED [ 81%]
tests/test_enrollments.py::test_list_and_delete_enrollment PASSED        [ 84%]
tests/test_main.py::test_root_view_html PASSED                           [ 87%]
tests/test_main.py::test_health_check PASSED                             [ 90%]
tests/test_progress.py::test_mark_lesson_completed PASSED                [ 93%]
tests/test_progress.py::test_student_progress_summary PASSED             [ 96%]
tests/test_progress.py::test_student_progress_list PASSED                [100%]

====================== 32 passed in 11.23s =======================
```

---

## 📁 Project Directory Structure

```
management-system/
│
├── app/
│   ├── config.py                 # Application settings and environment variables
│   ├── database.py               # SQLAlchemy database engine and session factory
│   ├── security.py               # Bcrypt password hashing & JWT token encoding/decoding
│   ├── main.py                   # FastAPI initialization, routing & middleware
│   │
│   ├── models/                   # SQLAlchemy ORM database models
│   │   ├── student.py            # Student user model
│   │   ├── course.py             # Course, Module & Lesson models
│   │   ├── enrollment.py         # Course enrollment model
│   │   ├── assessment.py         # Assessment, Question & StudentAnswer models
│   │   ├── progress.py           # Lesson completion progress model
│   │   └── result.py             # Assessment result model
│   │
│   ├── schemas/                  # Pydantic v2 validation models
│   │   ├── student.py            # Student schemas (Create, Login, Out)
│   │   ├── course.py             # Course & Curriculum schemas
│   │   ├── enrollment.py         # Enrollment schemas
│   │   ├── assessment.py         # Assessment & Question schemas
│   │   ├── progress.py           # Progress schemas
│   │   └── analytics.py          # Analytics & Chart schemas
│   │
│   ├── routers/                  # FastAPI REST API route handlers
│   │   ├── auth.py               # Student registration & JWT authentication
│   │   ├── students.py           # Student profile management
│   │   ├── courses.py            # Course & Module CRUD
│   │   ├── enrollments.py        # Enrollment management
│   │   ├── assessments.py        # Quiz creation & auto-grading
│   │   ├── progress.py           # Lesson completion tracking
│   │   └── analytics.py          # Pandas aggregations & Plotly charts
│   │
│   ├── services/                 # Core domain business logic
│   │   ├── assessment_service.py # Automated scoring & weak topic identification
│   │   ├── progress_service.py   # Completion calculation & inactivity detection
│   │   └── analytics_service.py  # Pandas statistics & Plotly JSON generators
│   │
│   └── templates/
│       └── index.html            # Responsive UI Dashboard with embedded modals & Plotly
│
├── database/
│   ├── schema.sql                # Pure SQL schema definition
│   └── seed_data.py              # Database seeding script with realistic dummy data
│
├── tests/                        # Pytest automated test suite (32 tests)
│   ├── conftest.py               # In-memory SQLite fixtures & HTTP test client
│   ├── test_analytics.py         # Analytics & Pandas endpoint tests
│   ├── test_assessments.py       # Quiz evaluation & scoring tests
│   ├── test_auth.py              # Registration, JWT & profile tests
│   ├── test_courses.py           # Course CRUD & module hierarchy tests
│   ├── test_enrollments.py       # Enrollment management tests
│   ├── test_main.py              # Root HTML view & health check tests
│   └── test_progress.py          # Lesson tracking & summary tests
│
├── .env.example                  # Environment configuration template
├── requirements.txt              # Project Python dependencies
├── run.py                        # Uvicorn server launcher
└── README.md                     # Project documentation
```

---

## 🔒 Security & Engineering Best Practices

- **Password Security**: Zero plain-text passwords. All credentials are encrypted using `bcrypt` with adaptive work factor salts.
- **Stateless Authentication**: JWT tokens signed using HS256 algorithm with configurable expiration window.
- **SQL Injection Prevention**: Completely mitigated through parameterized queries via SQLAlchemy 2.0 ORM.
- **Data Validation & Sanitization**: Strict Pydantic v2 schemas validating request payloads, data types, and constraints.
- **Error Handling**: Graceful exception handling ensuring clean JSON error responses across all endpoints.
