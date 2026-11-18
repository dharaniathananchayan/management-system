from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.course import Course, Module
from app.models.student import Student
from app.models.assessment import Assessment, Question
from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentUpdate,
    AssessmentOut,
    AssessmentDetailStudentOut,
    AssessmentDetailAdminOut,
    QuestionCreate,
    QuestionStudentOut,
    AssessmentSubmission,
    ResultOut,
)
from app.services.assessment_service import evaluate_submission
from app.security import get_current_student

router = APIRouter(prefix="/assessments", tags=["Quiz and Assessment Module"])


@router.post("", response_model=AssessmentOut, status_code=status.HTTP_201_CREATED)
def create_assessment(payload: AssessmentCreate, db: Session = Depends(get_db)):
    """
    Create a new assessment/quiz for a course.
    Can optionally include initial questions.
    """
    course = db.query(Course).filter(Course.course_id == payload.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {payload.course_id} not found."
        )

    assessment = Assessment(
        course_id=payload.course_id,
        title=payload.title.strip(),
        description=payload.description,
        total_marks=payload.total_marks,
        passing_percentage=payload.passing_percentage,
        duration_minutes=payload.duration_minutes,
    )
    db.add(assessment)
    db.flush()

    if payload.questions:
        for q_in in payload.questions:
            q = Question(
                module_id=q_in.module_id,
                assessment_id=assessment.assessment_id,
                question_text=q_in.question_text.strip(),
                question_type=q_in.question_type,
                options_json=None,  # will be set via options setter
                correct_answer=q_in.correct_answer.strip(),
                points=q_in.points,
                topic=q_in.topic,
            )
            q.options = q_in.options
            db.add(q)

    db.commit()
    db.refresh(assessment)

    return AssessmentOut(
        assessment_id=assessment.assessment_id,
        course_id=assessment.course_id,
        title=assessment.title,
        description=assessment.description,
        total_marks=assessment.total_marks,
        passing_percentage=assessment.passing_percentage,
        duration_minutes=assessment.duration_minutes,
        created_at=assessment.created_at,
        question_count=len(assessment.questions),
    )


@router.get("", response_model=List[AssessmentOut])
def list_assessments(
    course_id: Optional[int] = Query(None, description="Filter by course ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all assessments with question count."""
    query = db.query(Assessment)
    if course_id is not None:
        query = query.filter(Assessment.course_id == course_id)

    assessments = query.offset(skip).limit(limit).all()
    return [
        AssessmentOut(
            assessment_id=a.assessment_id,
            course_id=a.course_id,
            title=a.title,
            description=a.description,
            total_marks=a.total_marks,
            passing_percentage=a.passing_percentage,
            duration_minutes=a.duration_minutes,
            created_at=a.created_at,
            question_count=len(a.questions),
        )
        for a in assessments
    ]


@router.get("/{assessment_id}", response_model=AssessmentDetailStudentOut)
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    """
    Get assessment with its questions (Example Screen 3).
    Omits the correct_answer so students cannot inspect client responses to cheat.
    """
    assessment = db.query(Assessment).filter(Assessment.assessment_id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment with id {assessment_id} not found."
        )

    q_outs = [
        QuestionStudentOut(
            question_id=q.question_id,
            module_id=q.module_id,
            question_text=q.question_text,
            question_type=q.question_type,
            options=q.options,
            points=q.points,
            topic=q.topic,
        )
        for q in assessment.questions
    ]

    return AssessmentDetailStudentOut(
        assessment_id=assessment.assessment_id,
        course_id=assessment.course_id,
        title=assessment.title,
        description=assessment.description,
        total_marks=assessment.total_marks,
        passing_percentage=assessment.passing_percentage,
        duration_minutes=assessment.duration_minutes,
        created_at=assessment.created_at,
        question_count=len(assessment.questions),
        questions=q_outs,
    )


@router.post("/{assessment_id}/questions", response_model=QuestionStudentOut, status_code=status.HTTP_201_CREATED)
def add_question_to_assessment(
    assessment_id: int,
    payload: QuestionCreate,
    db: Session = Depends(get_db),
):
    """Add a question directly to an assessment."""
    assessment = db.query(Assessment).filter(Assessment.assessment_id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    q = Question(
        module_id=payload.module_id,
        assessment_id=assessment_id,
        question_text=payload.question_text.strip(),
        question_type=payload.question_type,
        correct_answer=payload.correct_answer.strip(),
        points=payload.points,
        topic=payload.topic,
    )
    q.options = payload.options
    db.add(q)
    db.commit()
    db.refresh(q)

    return QuestionStudentOut(
        question_id=q.question_id,
        module_id=q.module_id,
        question_text=q.question_text,
        question_type=q.question_type,
        options=q.options,
        points=q.points,
        topic=q.topic,
    )


@router.post("/{assessment_id}/submit", response_model=ResultOut)
def submit_assessment(
    assessment_id: int,
    submission: AssessmentSubmission,
    student_id_query: Optional[int] = Query(None, alias="student_id"),
    db: Session = Depends(get_db),
):
    """
    Submit student answers for automated evaluation.
    - Matches student answers to correct options
    - Calculates score, percentage, and pass/fail status
    - Identifies weak topics and generates targeted learning recommendations
    - Stores submission history in results table
    """
    target_student_id = submission.student_id or student_id_query
    if not target_student_id:
        # Fallback to first student if demo/testing without auth header
        first_student = db.query(Student).first()
        if first_student:
            target_student_id = first_student.student_id
        else:
            raise HTTPException(status_code=400, detail="Student ID must be specified.")

    student = db.query(Student).filter(Student.student_id == target_student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student {target_student_id} not found.")

    return evaluate_submission(
        db=db,
        assessment_id=assessment_id,
        submission=submission,
        student_id=target_student_id,
    )
