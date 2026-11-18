from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class TopicPerformance(BaseModel):
    topic: str
    total_questions: int
    correct_count: int
    accuracy_percentage: float
    difficulty_level: str  # "Hard", "Medium", "Easy"


class CourseAnalyticsOut(BaseModel):
    course_id: int
    course_name: str
    total_enrolled: int
    total_assessments: int
    total_submissions: int
    average_assessment_score: float
    average_completion_percentage: float
    passing_rate: float
    difficult_topics: List[TopicPerformance]
    grade_distribution: Dict[str, int]
    recommendations: List[str]


class InactiveStudentOut(BaseModel):
    student_id: int
    name: str
    email: str
    enrolled_courses: int
    completed_lessons: int
    last_activity_date: Optional[datetime] = None
    days_inactive: int
    risk_level: str  # "High", "Medium", "Low"


class LowPerformerOut(BaseModel):
    student_id: int
    name: str
    email: str
    course_id: int
    course_name: str
    average_score: float
    failing_assessments_count: int
    recommended_action: str


class DashboardAnalyticsOut(BaseModel):
    total_students: int
    total_courses: int
    total_modules: int
    total_lessons: int
    total_assessments: int
    total_enrollments: int
    overall_average_score: float
    active_students_count: int
    inactive_students_count: int
    course_averages: Dict[str, float]
    student_activity_trend: Dict[str, int]  # Day of week -> submissions / completions count
