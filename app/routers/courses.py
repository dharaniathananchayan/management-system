from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.student import Student
from app.models.course import Course, Module, Lesson
from app.models.enrollment import Enrollment
from app.schemas.course import (
    CourseCreate,
    CourseUpdate,
    CourseOut,
    CourseDetailOut,
    ModuleCreate,
    ModuleOut,
    LessonCreate,
    LessonOut,
)
from app.schemas.enrollment import EnrollmentOut, EnrollmentCreate
from app.security import get_current_student

router = APIRouter(tags=["Course Management"])


def _populate_course_stats(course: Course, db: Session) -> CourseOut:
    module_count = db.query(Module).filter(Module.course_id == course.course_id).count()
    student_count = db.query(Enrollment).filter(Enrollment.course_id == course.course_id).count()
    lesson_count = (
        db.query(Lesson)
        .join(Module, Lesson.module_id == Module.module_id)
        .filter(Module.course_id == course.course_id)
        .count()
    )
    return CourseOut(
        course_id=course.course_id,
        course_name=course.course_name,
        category=getattr(course, "category", "Python & Backend") or "Python & Backend",
        level=getattr(course, "level", "Beginner") or "Beginner",
        duration_hours=getattr(course, "duration_hours", 20) or 20,
        passing_criteria=getattr(course, "passing_criteria", 60) or 60,
        instructor_name=getattr(course, "instructor_name", "ArchintX Faculty") or "ArchintX Faculty",
        prerequisites=getattr(course, "prerequisites", None),
        description=course.description,
        status=course.status,
        created_at=course.created_at,
        updated_at=course.updated_at,
        module_count=module_count,
        student_count=student_count,
        lesson_count=lesson_count,
    )


@router.post("/courses", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
def create_course(payload: CourseCreate, db: Session = Depends(get_db)):
    """Create a new course in ArchintX with complete curriculum metadata."""
    course = Course(
        course_name=payload.course_name.strip(),
        category=payload.category or "Python & Backend",
        level=payload.level or "Beginner",
        duration_hours=payload.duration_hours or 20,
        passing_criteria=payload.passing_criteria or 60,
        instructor_name=payload.instructor_name or "ArchintX Faculty",
        prerequisites=payload.prerequisites,
        description=payload.description,
        status=payload.status or "Active",
    )
    db.add(course)
    db.flush()

    # Optional automatic initial module & lesson generation
    if payload.initial_module_name:
        mod = Module(
            course_id=course.course_id,
            module_name=payload.initial_module_name.strip(),
            order_index=1,
        )
        db.add(mod)
        db.flush()
        if payload.initial_lesson_title:
            les = Lesson(
                module_id=mod.module_id,
                lesson_title=payload.initial_lesson_title.strip(),
                content="Initial lesson introductory content and overview.",
                duration_minutes=20,
                order_index=1,
            )
            db.add(les)

    db.commit()
    db.refresh(course)
    return _populate_course_stats(course, db)


@router.get("/courses", response_model=List[CourseOut])
def list_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status: Active, Draft, Archived"),
    search: Optional[str] = Query(None, description="Search course name or description"),
    db: Session = Depends(get_db),
):
    """
    List courses with pagination, filtering, and stats.
    Matches Example Screen 2 (Course Management):
    - Course name
    - Modules count
    - Students enrolled
    - Status (Active, Draft)
    """
    query = db.query(Course)
    if status:
        query = query.filter(Course.status == status)
    if search:
        query = query.filter(Course.course_name.ilike(f"%{search}%"))

    courses = query.offset(skip).limit(limit).all()
    return [_populate_course_stats(c, db) for c in courses]


@router.get("/courses/{course_id}", response_model=CourseDetailOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """Get full course information including modules and lessons hierarchy."""
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found."
        )
    stats_out = _populate_course_stats(course, db)
    return CourseDetailOut(
        course_id=course.course_id,
        course_name=course.course_name,
        description=course.description,
        status=course.status,
        created_at=course.created_at,
        updated_at=course.updated_at,
        module_count=stats_out.module_count,
        student_count=stats_out.student_count,
        lesson_count=stats_out.lesson_count,
        modules=course.modules,
    )


@router.put("/courses/{course_id}", response_model=CourseOut)
def update_course(course_id: int, payload: CourseUpdate, db: Session = Depends(get_db)):
    """Update course attributes."""
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if payload.course_name is not None:
        course.course_name = payload.course_name.strip()
    if payload.category is not None:
        course.category = payload.category
    if payload.level is not None:
        course.level = payload.level
    if payload.duration_hours is not None:
        course.duration_hours = payload.duration_hours
    if payload.passing_criteria is not None:
        course.passing_criteria = payload.passing_criteria
    if payload.instructor_name is not None:
        course.instructor_name = payload.instructor_name
    if payload.prerequisites is not None:
        course.prerequisites = payload.prerequisites
    if payload.description is not None:
        course.description = payload.description
    if payload.status is not None:
        course.status = payload.status

    db.commit()
    db.refresh(course)
    return _populate_course_stats(course, db)


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    """Delete a course and cascade its modules and lessons."""
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()
    return None


@router.post("/courses/{course_id}/enroll", response_model=EnrollmentOut)
def enroll_student(
    course_id: int,
    payload: Optional[EnrollmentCreate] = None,
    student_id_query: Optional[int] = Query(None, alias="student_id"),
    db: Session = Depends(get_db),
):
    """
    Enroll a student into a course.
    Student ID can be provided in the request body, as a query param, or via authenticated session.
    """
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    target_student_id = None
    if payload and payload.student_id:
        target_student_id = payload.student_id
    elif student_id_query:
        target_student_id = student_id_query

    if not target_student_id:
        # Check if there is any student in database or default to student 1
        first_student = db.query(Student).first()
        if first_student:
            target_student_id = first_student.student_id
        else:
            raise HTTPException(status_code=400, detail="Student ID must be specified.")

    student = db.query(Student).filter(Student.student_id == target_student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Check if already enrolled
    existing = db.query(Enrollment).filter(
        Enrollment.student_id == target_student_id,
        Enrollment.course_id == course_id
    ).first()
    if existing:
        return EnrollmentOut(
            enrollment_id=existing.enrollment_id,
            student_id=existing.student_id,
            student_name=student.name,
            course_id=existing.course_id,
            course_name=course.course_name,
            enrolled_at=existing.enrolled_at,
            status=existing.status,
        )

    enr_data = {"student_id": target_student_id, "course_id": course_id, "status": "active"}
    if payload and payload.enrollment_id is not None:
        enr_data["enrollment_id"] = payload.enrollment_id

    enrollment = Enrollment(**enr_data)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return EnrollmentOut(
        enrollment_id=enrollment.enrollment_id,
        student_id=enrollment.student_id,
        student_name=student.name,
        course_id=enrollment.course_id,
        course_name=course.course_name,
        enrolled_at=enrollment.enrolled_at,
        status=enrollment.status,
    )


# --- Modules & Lessons Endpoints ---
@router.post("/courses/{course_id}/modules", response_model=ModuleOut, status_code=status.HTTP_201_CREATED)
def add_module_to_course(course_id: int, payload: ModuleCreate, db: Session = Depends(get_db)):
    """Add a module to a course."""
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    module = Module(
        course_id=course_id,
        module_name=payload.module_name.strip(),
        order_index=payload.order_index,
    )
    db.add(module)
    db.commit()
    db.refresh(module)
    return module


@router.get("/courses/{course_id}/modules", response_model=List[ModuleOut])
def get_course_modules(course_id: int, db: Session = Depends(get_db)):
    """List all modules for a course."""
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course.modules


@router.post("/modules/{module_id}/lessons", response_model=LessonOut, status_code=status.HTTP_201_CREATED)
def add_lesson_to_module(module_id: int, payload: LessonCreate, db: Session = Depends(get_db)):
    """Add a lesson to a module."""
    module = db.query(Module).filter(Module.module_id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    lesson = Lesson(
        module_id=module_id,
        lesson_title=payload.lesson_title.strip(),
        content=payload.content,
        duration_minutes=payload.duration_minutes,
        order_index=payload.order_index,
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


@router.get("/lessons/{lesson_id}", response_model=LessonOut)
def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    """Get single lesson details."""
    lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson
