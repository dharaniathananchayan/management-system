from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class EnrollmentBase(BaseModel):
    student_id: int = Field(..., example=1, description="ID of student enrolling")
    course_id: int = Field(..., example=1, description="ID of course to enroll in")


class EnrollmentCreate(EnrollmentBase):
    enrollment_id: Optional[int] = Field(
        None,
        example=101,
        description="Optional manual Enrollment ID (auto-generated if omitted)",
    )
    status: Optional[str] = Field("active", example="active")


class EnrollmentOut(BaseModel):
    enrollment_id: int
    student_id: int
    student_name: Optional[str] = None
    course_id: int
    course_name: Optional[str] = None
    enrolled_at: datetime
    status: str

    class Config:
        from_attributes = True
