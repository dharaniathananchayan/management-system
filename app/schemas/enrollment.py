from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class EnrollmentBase(BaseModel):
    course_id: int = Field(..., example=1)


class EnrollmentCreate(EnrollmentBase):
    student_id: Optional[int] = Field(None, example=1)


class EnrollmentOut(BaseModel):
    enrollment_id: int
    student_id: int
    course_id: int
    course_name: Optional[str] = None
    enrolled_at: datetime
    status: str

    class Config:
        from_attributes = True
