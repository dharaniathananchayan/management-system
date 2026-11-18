from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field


# --- Question Schemas ---
class QuestionBase(BaseModel):
    module_id: int = Field(..., example=1)
    assessment_id: Optional[int] = Field(None, example=1)
    question_text: str = Field(..., min_length=3, example="What is the output of: print(2 ** 3) ?")
    question_type: str = Field("multiple_choice", example="multiple_choice")  # multiple_choice, true_false, short_answer
    options: List[str] = Field(default=[], example=["6", "8", "9", "Error"])
    points: float = Field(1.0, ge=0.1, example=1.0)
    topic: Optional[str] = Field(None, example="Operators")


class QuestionCreate(QuestionBase):
    correct_answer: str = Field(..., example="8")


class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    question_type: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    points: Optional[float] = None
    topic: Optional[str] = None


class QuestionStudentOut(BaseModel):
    question_id: int
    module_id: int
    question_text: str
    question_type: str
    options: List[str]
    points: float
    topic: Optional[str] = None

    class Config:
        from_attributes = True


class QuestionAdminOut(QuestionStudentOut):
    correct_answer: str


# --- Assessment Schemas ---
class AssessmentBase(BaseModel):
    course_id: int = Field(..., example=1)
    title: str = Field(..., min_length=3, max_length=150, example="Python Assessment 1")
    description: Optional[str] = Field(None, example="Evaluation of Python core syntax, loops, and functions.")
    total_marks: float = Field(100.0, ge=1.0, example=100.0)
    passing_percentage: float = Field(60.0, ge=0.0, le=100.0, example=60.0)
    duration_minutes: int = Field(15, ge=1, le=300, example=15)


class AssessmentCreate(AssessmentBase):
    questions: Optional[List[QuestionCreate]] = []


class AssessmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    total_marks: Optional[float] = None
    passing_percentage: Optional[float] = None
    duration_minutes: Optional[int] = None


class AssessmentOut(AssessmentBase):
    assessment_id: int
    created_at: datetime
    question_count: int = 0

    class Config:
        from_attributes = True


class AssessmentDetailStudentOut(AssessmentOut):
    questions: List[QuestionStudentOut] = []


class AssessmentDetailAdminOut(AssessmentOut):
    questions: List[QuestionAdminOut] = []


# --- Submission & Result Schemas ---
class SubmitAnswerItem(BaseModel):
    question_id: int = Field(..., example=1)
    answer: str = Field(..., example="8")


class AssessmentSubmission(BaseModel):
    student_id: Optional[int] = Field(None, example=1)  # Can be inferred from JWT or passed explicitly
    answers: List[SubmitAnswerItem]


class StudentAnswerOut(BaseModel):
    answer_id: int
    question_id: int
    question_text: Optional[str] = None
    student_answer: str
    correct_answer: Optional[str] = None
    is_correct: bool
    marks_awarded: float
    points: Optional[float] = None
    topic: Optional[str] = None


class ResultOut(BaseModel):
    result_id: int
    student_id: int
    assessment_id: int
    assessment_title: Optional[str] = None
    course_name: Optional[str] = None
    score: float
    total_marks: float
    percentage: float
    passed: bool
    feedback: Optional[str] = None
    completed_at: datetime
    breakdown: Optional[List[StudentAnswerOut]] = None
    weak_topics: Optional[List[str]] = []
    recommendations: Optional[List[str]] = []

    class Config:
        from_attributes = True
