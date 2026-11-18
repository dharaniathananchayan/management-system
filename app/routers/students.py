from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.student import Student
from app.models.assessment import Result, Assessment
from app.schemas.student import StudentOut, StudentUpdate
from app.schemas.assessment import ResultOut, StudentAnswerOut
from app.schemas.progress import StudentProgressSummary
from app.services.progress_service import get_student_progress_summary
from app.security import get_current_student

router = APIRouter(prefix="/students", tags=["Student Management"])


@router.get("", response_model=List[StudentOut])
def list_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None, description="Filter by role: student, admin, instructor"),
    db: Session = Depends(get_db),
):
    """Retrieve paginated list of students."""
    query = db.query(Student)
    if role:
        query = query.filter(Student.role == role)
    return query.offset(skip).limit(limit).all()


@router.get("/{student_id}", response_model=StudentOut)
def get_student_details(student_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a specific student."""
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found."
        )
    return student


@router.put("/{student_id}", response_model=StudentOut)
def update_student(
    student_id: int,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
):
    """Update student profile details."""
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found."
        )

    if payload.name is not None:
        student.name = payload.name.strip()
    if payload.email is not None:
        new_email = payload.email.lower().strip()
        existing = db.query(Student).filter(
            Student.email == new_email,
            Student.student_id != student_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already used by another account."
            )
        student.email = new_email
    if payload.is_active is not None:
        student.is_active = payload.is_active

    db.commit()
    db.refresh(student)
    return student


@router.get("/{student_id}/results", response_model=List[ResultOut])
def get_student_results(
    student_id: int,
    passed_only: Optional[bool] = Query(None, description="Filter by pass/fail status"),
    db: Session = Depends(get_db),
):
    """
    Get all assessment test results and scores for a specific student,
    including detailed questions breakdown and feedback.
    """
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    query = db.query(Result).filter(Result.student_id == student_id)
    if passed_only is not None:
        query = query.filter(Result.passed == passed_only)

    results = query.order_by(Result.completed_at.desc()).all()
    output: List[ResultOut] = []

    for r in results:
        course_name = r.assessment.course.course_name if r.assessment and r.assessment.course else "Course"
        
        # Populate student answers breakdown
        breakdown: List[StudentAnswerOut] = []
        weak_topics: List[str] = []
        topic_scores = {}

        for ans in r.student.answers:
            if ans.assessment_id == r.assessment_id:
                t = ans.question.topic or "General"
                if t not in topic_scores:
                    topic_scores[t] = {"total": 0, "correct": 0}
                topic_scores[t]["total"] += 1
                if ans.is_correct:
                    topic_scores[t]["correct"] += 1

                breakdown.append(
                    StudentAnswerOut(
                        answer_id=ans.answer_id,
                        question_id=ans.question_id,
                        question_text=ans.question.question_text if ans.question else None,
                        student_answer=ans.answer,
                        correct_answer=ans.question.correct_answer if ans.question else None,
                        is_correct=ans.is_correct,
                        marks_awarded=ans.marks_awarded,
                        points=ans.question.points if ans.question else 1.0,
                        topic=t,
                    )
                )

        for topic, st in topic_scores.items():
            if st["total"] > 0 and (st["correct"] / st["total"]) < 0.6:
                weak_topics.append(topic)

        output.append(
            ResultOut(
                result_id=r.result_id,
                student_id=r.student_id,
                assessment_id=r.assessment_id,
                assessment_title=r.assessment.title if r.assessment else "Assessment",
                course_name=course_name,
                score=r.score,
                total_marks=r.assessment.total_marks if r.assessment else 100.0,
                percentage=r.percentage,
                passed=r.passed,
                feedback=r.feedback,
                completed_at=r.completed_at,
                breakdown=breakdown,
                weak_topics=weak_topics,
            )
        )

    return output


@router.get("/{student_id}/progress", response_model=StudentProgressSummary)
def get_student_learning_progress(student_id: int, db: Session = Depends(get_db)):
    """
    Get full learning progress metrics for a student.
    Matches Example Screen 1:
    - Enrolled Courses count
    - Completed Lessons count
    - Average assessment score
    - Per-course completion percentage bars
    """
    return get_student_progress_summary(db, student_id)
