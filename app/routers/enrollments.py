from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.student import Student
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.schemas.enrollment import EnrollmentCreate, EnrollmentOut

router = APIRouter(prefix="/enrollments", tags=["Enrollment Management"])


@router.post("", response_model=EnrollmentOut, status_code=status.HTTP_201_CREATED)
def create_enrollment(payload: EnrollmentCreate, db: Session = Depends(get_db)):
    """
    Enroll a student into a course using form/JSON fields:
    - `enrollment_id` (optional, auto-generated if omitted)
    - `student_id` (required)
    - `course_id` (required)
    """
    # Verify student exists
    student = db.query(Student).filter(Student.student_id == payload.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {payload.student_id} not found."
        )

    # Verify course exists
    course = db.query(Course).filter(Course.course_id == payload.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {payload.course_id} not found."
        )

    # Check for manual enrollment_id collision if provided
    if payload.enrollment_id is not None:
        existing_id = db.query(Enrollment).filter(Enrollment.enrollment_id == payload.enrollment_id).first()
        if existing_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Enrollment with ID {payload.enrollment_id} already exists."
            )

    # Check if student is already enrolled in this course
    existing_enr = db.query(Enrollment).filter(
        Enrollment.student_id == payload.student_id,
        Enrollment.course_id == payload.course_id,
    ).first()
    if existing_enr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student {student.name} (ID: {payload.student_id}) is already enrolled in '{course.course_name}'."
        )

    enrollment_kwargs = {
        "student_id": payload.student_id,
        "course_id": payload.course_id,
        "status": payload.status or "active",
        "enrolled_at": datetime.utcnow(),
    }
    if payload.enrollment_id is not None:
        enrollment_kwargs["enrollment_id"] = payload.enrollment_id

    enrollment = Enrollment(**enrollment_kwargs)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return EnrollmentOut(
        enrollment_id=enrollment.enrollment_id,
        student_id=student.student_id,
        student_name=student.name,
        course_id=course.course_id,
        course_name=course.course_name,
        enrolled_at=enrollment.enrolled_at,
        status=enrollment.status,
    )


@router.get("", response_model=List[EnrollmentOut])
def list_enrollments(
    student_id: Optional[int] = Query(None, description="Filter by Student ID"),
    course_id: Optional[int] = Query(None, description="Filter by Course ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all enrollments with student and course details."""
    query = db.query(Enrollment)
    if student_id is not None:
        query = query.filter(Enrollment.student_id == student_id)
    if course_id is not None:
        query = query.filter(Enrollment.course_id == course_id)

    enrollments = query.order_by(Enrollment.enrollment_id.desc()).offset(skip).limit(limit).all()

    return [
        EnrollmentOut(
            enrollment_id=e.enrollment_id,
            student_id=e.student_id,
            student_name=e.student.name if e.student else None,
            course_id=e.course_id,
            course_name=e.course.course_name if e.course else None,
            enrolled_at=e.enrolled_at,
            status=e.status,
        )
        for e in enrollments
    ]


@router.get("/{enrollment_id}", response_model=EnrollmentOut)
def get_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a specific enrollment."""
    enrollment = db.query(Enrollment).filter(Enrollment.enrollment_id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enrollment with ID {enrollment_id} not found."
        )
    return EnrollmentOut(
        enrollment_id=enrollment.enrollment_id,
        student_id=enrollment.student_id,
        student_name=enrollment.student.name if enrollment.student else None,
        course_id=enrollment.course_id,
        course_name=enrollment.course.course_name if enrollment.course else None,
        enrolled_at=enrollment.enrolled_at,
        status=enrollment.status,
    )


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    """Drop or cancel an enrollment."""
    enrollment = db.query(Enrollment).filter(Enrollment.enrollment_id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enrollment with ID {enrollment_id} not found."
        )
    db.delete(enrollment)
    db.commit()
    return None
