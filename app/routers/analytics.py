from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.analytics import (
    CourseAnalyticsOut,
    DashboardAnalyticsOut,
    InactiveStudentOut,
    LowPerformerOut,
)
from app.services.analytics_service import (
    get_course_analytics,
    get_inactive_students,
    get_low_performing_students,
    get_dashboard_analytics,
    generate_plotly_charts,
)

router = APIRouter(prefix="/analytics", tags=["Performance Analytics"])


@router.get("/course/{course_id}", response_model=CourseAnalyticsOut)
def course_analytics(course_id: int, db: Session = Depends(get_db)):
    """
    Get detailed learning and assessment analytics for a specific course:
    - Enrollment and submission count
    - Average assessment score (via Pandas)
    - Pass rate and grade distribution
    - Difficult topics breakdown with accuracy %
    - Tailored learning and instructional recommendations
    """
    return get_course_analytics(db, course_id)


@router.get("/dashboard", response_model=DashboardAnalyticsOut)
def platform_dashboard_analytics(db: Session = Depends(get_db)):
    """
    Get high-level platform analytics across all courses and students:
    - Total students, courses, modules, lessons, assessments
    - Overall average platform score
    - Active vs inactive student counts
    - Course-wise average scores
    - Student activity trend by weekday (Mon - Sun)
    """
    return get_dashboard_analytics(db)


@router.get("/inactive-students", response_model=List[InactiveStudentOut])
def list_inactive_students(
    days: int = Query(7, ge=1, le=180, description="Inactivity threshold in days"),
    db: Session = Depends(get_db),
):
    """
    Identify inactive students who have not completed lessons or assessments
    within the specified days threshold.
    """
    return get_inactive_students(db, days_threshold=days)


@router.get("/low-performers", response_model=List[LowPerformerOut])
def list_low_performing_students(
    threshold: float = Query(60.0, ge=0.0, le=100.0, description="Score percentage threshold"),
    db: Session = Depends(get_db),
):
    """
    Identify students with assessment scores below the specified threshold
    and suggest actionable support steps.
    """
    return get_low_performing_students(db, threshold_percentage=threshold)


@router.get("/charts")
def get_chart_data(db: Session = Depends(get_db)):
    """
    Returns Plotly figure dictionary definitions matching Example Screen 4:
    - Average assessment score by course (Bar Chart)
    - Student activity trend (Line Chart)
    """
    return generate_plotly_charts(db)
