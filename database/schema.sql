-- ====================================================================
-- ArchintX: Learning Progress & Assessment Management System
-- Database Schema (PostgreSQL / MySQL / SQLite compatible standard DDL)
-- ====================================================================

-- 1. Students Table
CREATE TABLE IF NOT EXISTS students (
    student_id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_students_email ON students(email);
CREATE INDEX IF NOT EXISTS idx_students_role ON students(role);

-- 2. Courses Table
CREATE TABLE IF NOT EXISTS courses (
    course_id SERIAL PRIMARY KEY,
    course_name VARCHAR(150) NOT NULL,
    category VARCHAR(80) DEFAULT 'Python & Backend',
    level VARCHAR(50) DEFAULT 'Beginner',
    duration_hours INTEGER DEFAULT 20,
    passing_criteria INTEGER DEFAULT 60,
    instructor_name VARCHAR(120) DEFAULT 'ArchintX Faculty',
    prerequisites VARCHAR(255),
    description TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'Active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_courses_name ON courses(course_name);
CREATE INDEX IF NOT EXISTS idx_courses_status ON courses(status);

-- 3. Modules Table
CREATE TABLE IF NOT EXISTS modules (
    module_id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    module_name VARCHAR(150) NOT NULL,
    order_index INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_modules_course_id ON modules(course_id);

-- 4. Lessons Table
CREATE TABLE IF NOT EXISTS lessons (
    lesson_id SERIAL PRIMARY KEY,
    module_id INTEGER NOT NULL REFERENCES modules(module_id) ON DELETE CASCADE,
    lesson_title VARCHAR(200) NOT NULL,
    content TEXT,
    duration_minutes INTEGER NOT NULL DEFAULT 15,
    order_index INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lessons_module_id ON lessons(module_id);

-- 5. Enrollments Table
CREATE TABLE IF NOT EXISTS enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    enrolled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    CONSTRAINT uq_student_course_enrollment UNIQUE (student_id, course_id)
);

CREATE INDEX IF NOT EXISTS idx_enrollments_student ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course ON enrollments(course_id);

-- 6. Assessments Table
CREATE TABLE IF NOT EXISTS assessments (
    assessment_id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    total_marks DOUBLE PRECISION NOT NULL DEFAULT 100.0,
    passing_percentage DOUBLE PRECISION NOT NULL DEFAULT 60.0,
    duration_minutes INTEGER NOT NULL DEFAULT 15,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_assessments_course_id ON assessments(course_id);

-- 7. Questions Table
CREATE TABLE IF NOT EXISTS questions (
    question_id SERIAL PRIMARY KEY,
    module_id INTEGER NOT NULL REFERENCES modules(module_id) ON DELETE CASCADE,
    assessment_id INTEGER REFERENCES assessments(assessment_id) ON DELETE SET NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL DEFAULT 'multiple_choice',
    options_json TEXT,
    correct_answer VARCHAR(255) NOT NULL,
    points DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    topic VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_questions_module_id ON questions(module_id);
CREATE INDEX IF NOT EXISTS idx_questions_assessment_id ON questions(assessment_id);
CREATE INDEX IF NOT EXISTS idx_questions_topic ON questions(topic);

-- 8. Student Answers Table
CREATE TABLE IF NOT EXISTS student_answers (
    answer_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    assessment_id INTEGER NOT NULL REFERENCES assessments(assessment_id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    answer TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE,
    marks_awarded DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_answers_student ON student_answers(student_id);
CREATE INDEX IF NOT EXISTS idx_answers_assessment ON student_answers(assessment_id);

-- 9. Results Table
CREATE TABLE IF NOT EXISTS results (
    result_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    assessment_id INTEGER NOT NULL REFERENCES assessments(assessment_id) ON DELETE CASCADE,
    score DOUBLE PRECISION NOT NULL,
    percentage DOUBLE PRECISION NOT NULL,
    passed BOOLEAN NOT NULL DEFAULT FALSE,
    feedback TEXT,
    completed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_results_student ON results(student_id);
CREATE INDEX IF NOT EXISTS idx_results_assessment ON results(assessment_id);

-- 10. Progress Table
CREATE TABLE IF NOT EXISTS progress (
    progress_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    lesson_id INTEGER NOT NULL REFERENCES lessons(lesson_id) ON DELETE CASCADE,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    completed_at TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_student_lesson_progress UNIQUE (student_id, lesson_id)
);

CREATE INDEX IF NOT EXISTS idx_progress_student ON progress(student_id);
CREATE INDEX IF NOT EXISTS idx_progress_lesson ON progress(lesson_id);


-- ====================================================================
-- KEY ARCHINTX ANALYTICAL & REPORTING SQL QUERIES
-- ====================================================================

-- Query A: Calculate course completion percentage for student #1
-- SELECT 
--     c.course_id,
--     c.course_name,
--     COUNT(l.lesson_id) AS total_lessons,
--     COUNT(p.progress_id) FILTER (WHERE p.status = 'completed') AS completed_lessons,
--     ROUND((COUNT(p.progress_id) FILTER (WHERE p.status = 'completed')::numeric / NULLIF(COUNT(l.lesson_id), 0)) * 100, 1) AS completion_percentage
-- FROM courses c
-- JOIN modules m ON c.course_id = m.course_id
-- JOIN lessons l ON m.module_id = l.module_id
-- LEFT JOIN progress p ON l.lesson_id = p.lesson_id AND p.student_id = 1
-- GROUP BY c.course_id, c.course_name;

-- Query B: Identify weak topics across course assessments (accuracy < 60%)
-- SELECT 
--     q.topic,
--     COUNT(sa.answer_id) AS total_answers,
--     SUM(CASE WHEN sa.is_correct THEN 1 ELSE 0 END) AS correct_answers,
--     ROUND((SUM(CASE WHEN sa.is_correct THEN 1 ELSE 0 END)::numeric / COUNT(sa.answer_id)) * 100, 1) AS topic_accuracy
-- FROM questions q
-- JOIN student_answers sa ON q.question_id = sa.question_id
-- GROUP BY q.topic
-- HAVING ROUND((SUM(CASE WHEN sa.is_correct THEN 1 ELSE 0 END)::numeric / COUNT(sa.answer_id)) * 100, 1) < 60
-- ORDER BY topic_accuracy ASC;

-- Query C: Inactive student monitoring (No activity within last 7 days)
-- SELECT 
--     s.student_id, 
--     s.name, 
--     s.email, 
--     MAX(COALESCE(p.updated_at, r.completed_at, s.created_at)) AS last_active
-- FROM students s
-- LEFT JOIN progress p ON s.student_id = p.student_id
-- LEFT JOIN results r ON s.student_id = r.student_id
-- WHERE s.role = 'student'
-- GROUP BY s.student_id, s.name, s.email
-- HAVING MAX(COALESCE(p.updated_at, r.completed_at, s.created_at)) < NOW() - INTERVAL '7 days';
