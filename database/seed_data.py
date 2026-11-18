import os
import sys
from datetime import datetime, timezone, timedelta

# Ensure parent directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal, Base
from app.models.student import Student
from app.models.course import Course, Module, Lesson
from app.models.enrollment import Enrollment
from app.models.assessment import Assessment, Question, StudentAnswer, Result
from app.models.progress import Progress
from app.security import hash_password


def seed_database():
    print("Dropping existing tables and creating fresh schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        print("Seeding Students...")
        
        # 1. Students
        s1 = Student(
            name="Alex Rivera",
            email="alex.rivera@example.com",
            password_hash=hash_password("student123"),
            role="student",
            is_active=True,
            created_at=now - timedelta(days=20),
        )
        s2 = Student(
            name="Samira Khan",
            email="samira.k@example.com",
            password_hash=hash_password("student123"),
            role="student",
            is_active=True,
            created_at=now - timedelta(days=15),
        )
        s3 = Student(
            name="David Chen",
            email="david.chen@example.com",
            password_hash=hash_password("student123"),
            role="student",
            is_active=True,
            created_at=now - timedelta(days=25),
        )
        s4 = Student(
            name="Inactive Student",
            email="inactive.user@example.com",
            password_hash=hash_password("student123"),
            role="student",
            is_active=True,
            created_at=now - timedelta(days=30),
        )
        admin = Student(
            name="Instructor Sarah",
            email="admin@example.com",
            password_hash=hash_password("admin123"),
            role="admin",
            is_active=True,
            created_at=now - timedelta(days=40),
        )
        db.add_all([s1, s2, s3, s4, admin])
        db.commit()

        print("Seeding Courses, Modules, and Lessons...")
        # 2. Courses (Matching Example 2 Mockup: Python Fundamentals (8 modules), SQL (6), API (5), Data Analytics (7))
        c1 = Course(
            course_name="Python Fundamentals",
            category="Python & Backend",
            level="Beginner",
            duration_hours=30,
            passing_criteria=60,
            instructor_name="Dr. Alan Foster",
            prerequisites="None (Beginner friendly)",
            description="Complete foundation in Python syntax, data structures, and object-oriented programming.",
            status="Active",
        )
        c2 = Course(
            course_name="SQL for Beginners",
            category="Database & SQL",
            level="Beginner",
            duration_hours=20,
            passing_criteria=65,
            instructor_name="Priya Sharma",
            prerequisites="Basic computer literacy",
            description="Relational database queries, joins, aggregations, and performance indexing.",
            status="Active",
        )
        c3 = Course(
            course_name="API Development",
            category="Web Development",
            level="Intermediate",
            duration_hours=25,
            passing_criteria=70,
            instructor_name="Sarah Jenkins",
            prerequisites="Python Fundamentals",
            description="Building high-performance REST APIs with FastAPI, Pydantic, and JWT authentication.",
            status="Draft",
        )
        c4 = Course(
            course_name="Data Analytics",
            category="Data Science & AI",
            level="Advanced",
            duration_hours=35,
            passing_criteria=75,
            instructor_name="Marcus Vance",
            prerequisites="Python & SQL Basics",
            description="Exploratory data analysis, Pandas manipulation, and Plotly visualization techniques.",
            status="Active",
        )
        db.add_all([c1, c2, c3, c4])
        db.commit()

        # Helper to create modules and lessons
        def create_modules_and_lessons(course, count, module_prefix, lessons_per_mod=2):
            all_lessons = []
            for i in range(1, count + 1):
                mod = Module(
                    course_id=course.course_id,
                    module_name=f"{module_prefix} Module {i}",
                    order_index=i,
                )
                db.add(mod)
                db.flush()
                for j in range(1, lessons_per_mod + 1):
                    les = Lesson(
                        module_id=mod.module_id,
                        lesson_title=f"{module_prefix} Lesson {i}.{j}: Key Principles",
                        content=f"Detailed study material and exercises for {module_prefix} module {i}, lesson {j}.",
                        duration_minutes=20,
                        order_index=j,
                    )
                    db.add(les)
                    all_lessons.append(les)
            db.commit()
            return all_lessons

        c1_lessons = create_modules_and_lessons(c1, 8, "Python", lessons_per_mod=2)   # 16 lessons
        c2_lessons = create_modules_and_lessons(c2, 6, "SQL", lessons_per_mod=2)      # 12 lessons
        c3_lessons = create_modules_and_lessons(c3, 5, "Web Dev", lessons_per_mod=2)  # 10 lessons
        c4_lessons = create_modules_and_lessons(c4, 7, "Data", lessons_per_mod=2)     # 14 lessons

        print("Seeding Enrollments...")
        # Enroll Alex Rivera in all 4 courses (matching Example 1: Enrolled Courses = 4)
        for c in [c1, c2, c3, c4]:
            db.add(Enrollment(student_id=s1.student_id, course_id=c.course_id, status="active"))
        # Enroll Samira Khan
        db.add(Enrollment(student_id=s2.student_id, course_id=c1.course_id, status="active"))
        db.add(Enrollment(student_id=s2.student_id, course_id=c2.course_id, status="active"))
        # Enroll David Chen
        db.add(Enrollment(student_id=s3.student_id, course_id=c1.course_id, status="active"))
        db.add(Enrollment(student_id=s3.student_id, course_id=c4.course_id, status="active"))
        # Enroll Inactive Student
        db.add(Enrollment(student_id=s4.student_id, course_id=c1.course_id, status="active"))
        db.commit()

        print("Seeding Progress Records...")
        # Exactly 18 completed lessons for Alex Rivera (matching Example 1 Mockup!):
        # 12 in Python, 4 in SQL, 2 in Web Dev = 18 completed lessons!
        for idx, l in enumerate(c1_lessons[:12]):
            db.add(Progress(student_id=s1.student_id, lesson_id=l.lesson_id, status="completed", completed_at=now - timedelta(days=12 - idx), updated_at=now - timedelta(days=12 - idx)))
        for l in c1_lessons[12:]:
            db.add(Progress(student_id=s1.student_id, lesson_id=l.lesson_id, status="pending", updated_at=now - timedelta(days=1)))

        for idx, l in enumerate(c2_lessons[:4]):
            db.add(Progress(student_id=s1.student_id, lesson_id=l.lesson_id, status="completed", completed_at=now - timedelta(days=8 - idx), updated_at=now - timedelta(days=8 - idx)))
        for l in c2_lessons[4:]:
            db.add(Progress(student_id=s1.student_id, lesson_id=l.lesson_id, status="pending", updated_at=now - timedelta(days=1)))

        for idx, l in enumerate(c3_lessons[:2]):
            db.add(Progress(student_id=s1.student_id, lesson_id=l.lesson_id, status="completed", completed_at=now - timedelta(days=4 - idx), updated_at=now - timedelta(days=4 - idx)))
        for l in c3_lessons[2:]:
            db.add(Progress(student_id=s1.student_id, lesson_id=l.lesson_id, status="pending", updated_at=now - timedelta(days=1)))

        # Also add progress for s2 and s3
        for idx, l in enumerate(c1_lessons[:8]):
            db.add(Progress(student_id=s2.student_id, lesson_id=l.lesson_id, status="completed", completed_at=now - timedelta(days=idx), updated_at=now - timedelta(days=idx)))
        for idx, l in enumerate(c4_lessons[:6]):
            db.add(Progress(student_id=s3.student_id, lesson_id=l.lesson_id, status="completed", completed_at=now - timedelta(days=idx), updated_at=now - timedelta(days=idx)))

        db.commit()

        print("Seeding Assessments and Questions...")
        # Assessment 1: Python Assessment (Matching Example 3 Mockup!)
        a1 = Assessment(
            course_id=c1.course_id,
            title="Python Assessment",
            description="Comprehensive assessment on Python syntax, operators, functions, and control structures.",
            total_marks=100.0,
            passing_percentage=60.0,
            duration_minutes=15,
        )
        db.add(a1)
        db.flush()

        # Questions for Assessment 1 (Matching Example 3 Mockup!)
        q_data = [
            (
                "What is the output of: print(2 ** 3) ?",
                ["6", "8", "9", "Error"],
                "8",
                "Operators",
                10.0,
            ),
            (
                "Which keyword is used to define a function in Python?",
                ["func", "def", "function", "lambda"],
                "def",
                "Functions",
                10.0,
            ),
            (
                "What is the correct syntax to output 'Hello World' in Python?",
                ["echo('Hello World')", "p('Hello World')", "print('Hello World')", "sys.out('Hello World')"],
                "print('Hello World')",
                "Syntax Basics",
                10.0,
            ),
            (
                "Which data type is immutable in Python?",
                ["List", "Dictionary", "Set", "Tuple"],
                "Tuple",
                "Data Types",
                10.0,
            ),
            (
                "How do you start a FOR loop in Python?",
                ["for x in y:", "for (x in y)", "foreach x in y", "loop x to y:"],
                "for x in y:",
                "Control Flow",
                10.0,
            ),
            (
                "What is the output of: len(['apple', 'banana', 'cherry']) ?",
                ["2", "3", "4", "Error"],
                "3",
                "Lists",
                10.0,
            ),
            (
                "Which method can be used to remove any whitespace from both the beginning and the end of a string?",
                ["trim()", "strip()", "ptrim()", "len()"],
                "strip()",
                "Strings",
                10.0,
            ),
            (
                "How do you handle exceptions in Python?",
                ["try...catch", "try...except", "do...while", "catch...throw"],
                "try...except",
                "Exceptions",
                10.0,
            ),
            (
                "What is the result of bool(0) in Python?",
                ["True", "False", "None", "Error"],
                "False",
                "Boolean Logic",
                10.0,
            ),
            (
                "Which operator is used to check equality in Python?",
                ["=", "==", "===", "!="],
                "==",
                "Operators",
                10.0,
            ),
        ]

        first_mod = c1.modules[0]
        q_objs = []
        for q_text, opts, corr, top, pts in q_data:
            q = Question(
                module_id=first_mod.module_id,
                assessment_id=a1.assessment_id,
                question_text=q_text,
                question_type="multiple_choice",
                correct_answer=corr,
                points=pts,
                topic=top,
            )
            q.options = opts
            db.add(q)
            q_objs.append(q)
        db.commit()

        # Assessment 2: SQL Beginner Assessment
        a2 = Assessment(
            course_id=c2.course_id,
            title="SQL Beginner Assessment",
            description="Testing SELECT, WHERE, JOIN, and GROUP BY clauses.",
            total_marks=100.0,
            passing_percentage=60.0,
            duration_minutes=20,
        )
        db.add(a2)
        db.flush()

        sql_mod = c2.modules[0]
        q_sql = [
            ("Which SQL statement is used to extract data from a database?", ["GET", "EXTRACT", "SELECT", "PULL"], "SELECT", "SQL Queries", 25.0),
            ("Which SQL clause is used to filter records?", ["FILTER", "WHERE", "ORDER BY", "HAVING"], "WHERE", "Filtering", 25.0),
            ("Which keyword is used to sort the result-set?", ["SORT BY", "ORDER", "ORDER BY", "ARRANGE"], "ORDER BY", "Sorting", 25.0),
            ("Which join returns all records when there is a match in either left or right table?", ["INNER JOIN", "LEFT JOIN", "FULL OUTER JOIN", "RIGHT JOIN"], "FULL OUTER JOIN", "Joins", 25.0),
        ]
        for q_text, opts, corr, top, pts in q_sql:
            q = Question(
                module_id=sql_mod.module_id,
                assessment_id=a2.assessment_id,
                question_text=q_text,
                question_type="multiple_choice",
                correct_answer=corr,
                points=pts,
                topic=top,
            )
            q.options = opts
            db.add(q)
        db.commit()

        # Assessment 3: Web Dev Assessment
        a3 = Assessment(
            course_id=c3.course_id,
            title="API & Web Development Assessment",
            description="Testing HTTP protocols, REST conventions, and status codes.",
            total_marks=100.0,
            passing_percentage=60.0,
            duration_minutes=15,
        )
        db.add(a3)
        db.flush()

        web_mod = c3.modules[0]
        q_web = [
            ("What HTTP status code denotes a successful resource creation?", ["200", "201", "204", "301"], "201", "HTTP Statuses", 50.0),
            ("Which HTTP method is typically used to update an existing resource completely?", ["GET", "POST", "PUT", "DELETE"], "PUT", "REST Principles", 50.0),
        ]
        for q_text, opts, corr, top, pts in q_web:
            q = Question(
                module_id=web_mod.module_id,
                assessment_id=a3.assessment_id,
                question_text=q_text,
                question_type="multiple_choice",
                correct_answer=corr,
                points=pts,
                topic=top,
            )
            q.options = opts
            db.add(q)
        db.commit()

        # Assessment 4: Data Analytics Assessment
        a4 = Assessment(
            course_id=c4.course_id,
            title="Data Analytics & Pandas Evaluation",
            description="Testing DataFrame manipulations, grouping, and aggregations.",
            total_marks=100.0,
            passing_percentage=60.0,
            duration_minutes=25,
        )
        db.add(a4)
        db.flush()

        data_mod = c4.modules[0]
        q_data_analytics = [
            ("Which Pandas function is used to read a CSV file?", ["read_table()", "read_csv()", "load_csv()", "import_csv()"], "read_csv()", "Data Ingestion", 50.0),
            ("Which method summarizes statistics of numeric columns in a DataFrame?", ["summary()", "describe()", "info()", "stats()"], "describe()", "Data Profiling", 50.0),
        ]
        for q_text, opts, corr, top, pts in q_data_analytics:
            q = Question(
                module_id=data_mod.module_id,
                assessment_id=a4.assessment_id,
                question_text=q_text,
                question_type="multiple_choice",
                correct_answer=corr,
                points=pts,
                topic=top,
            )
            q.options = opts
            db.add(q)
        db.commit()

        print("Seeding Assessment Results and Answers...")
        # Alex Rivera: Average score = 82% (matching Example 1!)
        # 80% on Python Assessment, 84% on SQL Assessment => (80 + 84)/2 = 82%!
        r1 = Result(
            student_id=s1.student_id,
            assessment_id=a1.assessment_id,
            score=80.0,
            percentage=80.0,
            passed=True,
            feedback="Passed with 80%! Solid grasp of core Python syntax.",
            completed_at=now - timedelta(days=4),
        )
        r2 = Result(
            student_id=s1.student_id,
            assessment_id=a2.assessment_id,
            score=84.0,
            percentage=84.0,
            passed=True,
            feedback="Passed with 84%! Strong performance in queries and filtering.",
            completed_at=now - timedelta(days=2),
        )
        db.add_all([r1, r2])

        # Samira Khan's results
        r3 = Result(
            student_id=s2.student_id,
            assessment_id=a1.assessment_id,
            score=64.0,
            percentage=64.0,
            passed=True,
            feedback="Passed with 64%. Needs improvement on exception handling.",
            completed_at=now - timedelta(days=3),
        )
        r4 = Result(
            student_id=s2.student_id,
            assessment_id=a2.assessment_id,
            score=84.0,
            percentage=84.0,
            passed=True,
            feedback="Passed with 84%.",
            completed_at=now - timedelta(days=1),
        )
        db.add_all([r3, r4])

        # David Chen's results: Web 68%, Data 91% (matching Example 4 course scores!)
        r5 = Result(
            student_id=s3.student_id,
            assessment_id=a3.assessment_id,
            score=68.0,
            percentage=68.0,
            passed=True,
            feedback="Passed with 68%. Review HTTP status codes.",
            completed_at=now - timedelta(days=5),
        )
        r6 = Result(
            student_id=s3.student_id,
            assessment_id=a4.assessment_id,
            score=91.0,
            percentage=91.0,
            passed=True,
            feedback="Passed with 91%! Outstanding data manipulation proficiency.",
            completed_at=now - timedelta(days=1),
        )
        db.add_all([r5, r6])
        db.commit()

        # Seed student answers for a1 so that weak topic calculation works
        for q in q_objs:
            corr = q.correct_answer
            is_cor = q.topic not in ["Exceptions", "Lists"]
            ans_val = corr if is_cor else "wrong_ans"
            sa = StudentAnswer(
                student_id=s1.student_id,
                assessment_id=a1.assessment_id,
                question_id=q.question_id,
                answer=ans_val,
                is_correct=is_cor,
                marks_awarded=q.points if is_cor else 0.0,
                submitted_at=now - timedelta(days=4),
            )
            db.add(sa)

        db.commit()
        print("Database seeded successfully with rich realistic ArchintX platform data!")

    except Exception as e:
        db.rollback()
        print("Error during seed:", e)
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
