from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class StudentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120, example="John Doe")
    email: EmailStr = Field(..., example="john.doe@example.com")


class StudentCreate(StudentBase):
    password: str = Field(..., min_length=6, max_length=100, example="securePassword123")
    role: Optional[str] = Field("student", example="student")


class StudentLogin(BaseModel):
    email: EmailStr = Field(..., example="john.doe@example.com")
    password: str = Field(..., example="securePassword123")


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=120)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class StudentOut(StudentBase):
    student_id: int
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    student: StudentOut
