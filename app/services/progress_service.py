from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.student import Student
from app.models.course import Course, Module, Lesson
from app.models.enrollment import Enrollment
from app.models.progress import Progress
from app.models.assessment import Result, Assessment
from app.schemas.progress import CourseProgressItem, StudentProgressSummary, ProgressOut


def mark_lesson_progress(
    db: Session,
    student_id: int,
    lesson_id: int,
    status_str: str = "completed"
) -> ProgressOut:
    """Mark a lesson as pending or completed for a student."""
    lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id {lesson_id} not found."
        )

    # Check if enrollment exists for this course
    course_id = lesson.module.course_id
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.course_id == course_id,
    ).first()
    if not enrollment:
        # Automatically enroll student or let them progress
        enrollment = Enrollment(student_id=student_id, course_id=course_id, status="active")
        db.add(enrollment)
        db.flush()

    progress = db.query(Progress).filter(
        Progress.student_id == student_id,
        Progress.lesson_id == lesson_id,
    ).first()

    now = datetime.utcnow()
    if not progress:
        progress = Progress(
            student_id=student_id,
            lesson_id=lesson_id,
            status=status_str,
            completed_at=now if status_str == "completed" else None,
            updated_at=now,
        )
        db.add(progress)
    else:
        progress.status = status_str
        progress.updated_at = now
        if status_str == "completed" and not progress.completed_at:
            progress.completed_at = now
        elif status_str != "completed":
            progress.completed_at = None

    db.commit()
    db.refresh(progress)

    return ProgressOut(
        progress_id=progress.progress_id,
        student_id=progress.student_id,
        lesson_id=progress.lesson_id,
        lesson_title=lesson.lesson_title,
        course_id=course_id,
        course_name=lesson.module.course.course_name,
        status=progress.status,
        completed_at=progress.completed_at,
        updated_at=progress.updated_at,
    )


def calculate_course_completion(db: Session, student_id: int, course_id: int) -> Dict[str, Any]:
    """Calculate progress percentage and counts for a specific course."""
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    total_lessons = (
        db.query(func.count(Lesson.lesson_id))
        .join(Module, Lesson.module_id == Module.module_id)
        .filter(Module.course_id == course_id)
        .scalar()
        or 0
    )

    completed_lessons = (
        db.query(func.count(Progress.progress_id))
        .join(Lesson, Progress.lesson_id == Lesson.lesson_id)
        .join(Module, Lesson.module_id == Module.module_id)
        .filter(
            Progress.student_id == student_id,
            Progress.status == "completed",
            Module.course_id == course_id,
        )
        .scalar()
        or 0
    )

    percentage = round((completed_lessons / total_lessons * 100.0), 1) if total_lessons > 0 else 0.0

    return {
        "course_id": course.course_id,
        "course_name": course.course_name,
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "completion_percentage": min(percentage, 100.0),
    }


def get_student_progress_summary(db: Session, student_id: int) -> StudentProgressSummary:
    """
    Generate comprehensive progress report for a student,
    matching the format and metrics of Example Screen 1.
    """
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found."
        )

    # Enrolled courses
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == student_id).all()
    enrolled_courses_count = len(enrollments)

    # Completed lessons across all courses
    completed_lessons_count = (
        db.query(func.count(Progress.progress_id))
        .filter(Progress.student_id == student_id, Progress.status == "completed")
        .scalar()
        or 0
    )

    # Average assessment score
    results = db.query(Result).filter(Result.student_id == student_id).all()
    if results:
        average_score = round(sum(r.percentage for r in results) / len(results), 1)
    else:
        average_score = 0.0

    # Per-course breakdown
    course_progress_list: List[CourseProgressItem] = []
    for enr in enrollments:
        stats = calculate_course_completion(db, student_id, enr.course_id)
        course_progress_list.append(
            CourseProgressItem(
                course_id=stats["course_id"],
                course_name=stats["course_name"],
                total_lessons=stats["total_lessons"],
                completed_lessons=stats["completed_lessons"],
                completion_percentage=stats["completion_percentage"],
            )
        )

    # Check inactivity (no lesson completion or assessment result in last 7 days)
    last_prog = (
        db.query(func.max(Progress.updated_at))
        .filter(Progress.student_id == student_id)
        .scalar()
    )
    last_result = (
        db.query(func.max(Result.completed_at))
        .filter(Result.student_id == student_id)
        .scalar()
    )

    dates = [d for d in [last_prog, last_result, student.created_at] if d is not None]
    most_recent = max(dates) if dates else student.created_at
    is_inactive = (datetime.utcnow() - most_recent) > timedelta(days=7)

    recent_assessments = [
        {
            "result_id": r.result_id,
            "assessment_id": r.assessment_id,
            "title": r.assessment.title if r.assessment else "Assessment",
            "score": r.score,
            "percentage": r.percentage,
            "passed": r.passed,
            "completed_at": r.completed_at.isoformat(),
        }
        for r in results[-5:]
    ]

    return StudentProgressSummary(
        student_id=student.student_id,
        student_name=student.name,
        enrolled_courses_count=enrolled_courses_count,
        completed_lessons_count=completed_lessons_count,
        average_score=average_score,
        course_progress=course_progress_list,
        recent_assessments=recent_assessments,
        is_inactive=is_inactive,
    )
