from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# --- Lesson Schemas ---
class LessonBase(BaseModel):
    lesson_title: str = Field(..., min_length=2, max_length=200, example="Introduction to Variables")
    content: Optional[str] = Field(None, example="Variables store data values...")
    duration_minutes: int = Field(15, ge=1, le=600, example=20)
    order_index: int = Field(1, ge=1, example=1)


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    lesson_title: Optional[str] = None
    content: Optional[str] = None
    duration_minutes: Optional[int] = None
    order_index: Optional[int] = None


class LessonOut(LessonBase):
    lesson_id: int
    module_id: int
    created_at: datetime
    is_completed: Optional[bool] = False

    class Config:
        from_attributes = True


# --- Module Schemas ---
class ModuleBase(BaseModel):
    module_name: str = Field(..., min_length=2, max_length=150, example="Python Syntax and Basics")
    order_index: int = Field(1, ge=1, example=1)


class ModuleCreate(ModuleBase):
    pass


class ModuleUpdate(BaseModel):
    module_name: Optional[str] = None
    order_index: Optional[int] = None


class ModuleOut(ModuleBase):
    module_id: int
    course_id: int
    created_at: datetime
    lessons: List[LessonOut] = []

    class Config:
        from_attributes = True


# --- Course Schemas ---
class CourseBase(BaseModel):
    course_name: str = Field(..., min_length=2, max_length=150, example="Python Fundamentals")
    category: Optional[str] = Field("Python & Backend", example="Python & Backend")
    level: Optional[str] = Field("Beginner", example="Beginner")  # Beginner, Intermediate, Advanced
    duration_hours: Optional[int] = Field(20, ge=1, le=500, example=24)
    passing_criteria: Optional[int] = Field(60, ge=40, le=100, example=60)
    instructor_name: Optional[str] = Field("Senior Faculty", example="Sarah Jenkins")
    prerequisites: Optional[str] = Field(None, example="Basic programming logic")
    description: Optional[str] = Field(None, example="Master the basics of Python programming.")
    status: str = Field("Active", example="Active")  # Active, Draft, Archived


class CourseCreate(CourseBase):
    initial_module_name: Optional[str] = Field(None, example="Module 1: Orientation & Setup")
    initial_lesson_title: Optional[str] = Field(None, example="Lesson 1.1: Environment Setup")


class CourseUpdate(BaseModel):
    course_name: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    duration_hours: Optional[int] = None
    passing_criteria: Optional[int] = None
    instructor_name: Optional[str] = None
    prerequisites: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class CourseOut(CourseBase):
    course_id: int
    created_at: datetime
    updated_at: datetime
    module_count: int = 0
    student_count: int = 0
    lesson_count: int = 0

    class Config:
        from_attributes = True


class CourseDetailOut(CourseOut):
    modules: List[ModuleOut] = []
