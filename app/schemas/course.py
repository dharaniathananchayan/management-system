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
    description: Optional[str] = Field(None, example="Master the basics of Python programming.")
    status: str = Field("Active", example="Active")  # Active, Draft, Archived


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    course_name: Optional[str] = None
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
