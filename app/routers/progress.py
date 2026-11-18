from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.student import Student
from app.models.progress import Progress
from app.schemas.progress import ProgressUpdate, ProgressOut
from app.services.progress_service import mark_lesson_progress
from app.security import get_current_student

router = APIRouter(prefix="/progress", tags=["Learning Progress Tracking"])


@router.post("/lessons/{lesson_id}", response_model=ProgressOut)
def update_lesson_progress(
    lesson_id: int,
    payload: ProgressUpdate,
    db: Session = Depends(get_db),
):
    """
    Update lesson completion status (completed / pending) for a student.
    """
    target_student_id = payload.student_id
    if not target_student_id:
        first_student = db.query(Student).first()
        if first_student:
            target_student_id = first_student.student_id
        else:
            raise HTTPException(status_code=400, detail="Student ID required.")

    return mark_lesson_progress(
        db=db,
        student_id=target_student_id,
        lesson_id=lesson_id,
        status_str=payload.status or "completed",
    )


@router.get("/student/{student_id}", response_model=List[ProgressOut])
def get_student_progress_list(
    student_id: int,
    status: Optional[str] = Query(None, description="Filter by status: completed or pending"),
    db: Session = Depends(get_db),
):
    """List all lesson progress records for a student."""
    query = db.query(Progress).filter(Progress.student_id == student_id)
    if status:
        query = query.filter(Progress.status == status)
    
    records = query.all()
    out: List[ProgressOut] = []
    for p in records:
        lesson = p.lesson
        course = lesson.module.course if lesson and lesson.module else None
        out.append(
            ProgressOut(
                progress_id=p.progress_id,
                student_id=p.student_id,
                lesson_id=p.lesson_id,
                lesson_title=lesson.lesson_title if lesson else "Lesson",
                course_id=course.course_id if course else None,
                course_name=course.course_name if course else None,
                status=p.status,
                completed_at=p.completed_at,
                updated_at=p.updated_at,
            )
        )
    return out
