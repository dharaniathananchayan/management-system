from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ProgressUpdate(BaseModel):
    student_id: Optional[int] = Field(None, example=1)
    status: str = Field("completed", example="completed")  # pending, completed


class ProgressOut(BaseModel):
    progress_id: int
    student_id: int
    lesson_id: int
    lesson_title: Optional[str] = None
    course_id: Optional[int] = None
    course_name: Optional[str] = None
    status: str
    completed_at: Optional[datetime] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class CourseProgressItem(BaseModel):
    course_id: int
    course_name: str
    total_lessons: int
    completed_lessons: int
    completion_percentage: float  # e.g., 78.0


class StudentProgressSummary(BaseModel):
    student_id: int
    student_name: str
    enrolled_courses_count: int
    completed_lessons_count: int
    average_score: float
    course_progress: List[CourseProgressItem]
    recent_assessments: List[dict] = []
    is_inactive: bool = False
