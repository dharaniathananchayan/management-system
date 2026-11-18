import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Question(Base):
    __tablename__ = "questions"

    question_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    module_id = Column(Integer, ForeignKey("modules.module_id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.assessment_id", ondelete="SET NULL"), nullable=True, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), default="multiple_choice", nullable=False)  # multiple_choice, true_false, short_answer
    options_json = Column(Text, nullable=True)  # JSON-encoded array of options: ["6", "8", "9", "Error"]
    correct_answer = Column(String(255), nullable=False)
    points = Column(Float, default=1.0, nullable=False)
    topic = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Helper properties for options
    @property
    def options(self):
        if self.options_json:
            try:
                return json.loads(self.options_json)
            except Exception:
                return []
        return []

    @options.setter
    def options(self, value):
        if isinstance(value, list):
            self.options_json = json.dumps(value)
        elif isinstance(value, str):
            self.options_json = value
        else:
            self.options_json = json.dumps([])

    # Relationships
    module = relationship("Module", back_populates="questions")
    assessment = relationship("Assessment", back_populates="questions")
    student_answers = relationship("StudentAnswer", back_populates="question", cascade="all, delete-orphan")


class Assessment(Base):
    __tablename__ = "assessments"

    assessment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    total_marks = Column(Float, default=100.0, nullable=False)
    passing_percentage = Column(Float, default=60.0, nullable=False)
    duration_minutes = Column(Integer, default=15, nullable=False)  # e.g., 15 mins for timer shown in mockup
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="assessments")
    questions = relationship("Question", back_populates="assessment", cascade="all, delete-orphan")
    results = relationship("Result", back_populates="assessment", cascade="all, delete-orphan")
    student_answers = relationship("StudentAnswer", back_populates="assessment", cascade="all, delete-orphan")


class StudentAnswer(Base):
    __tablename__ = "student_answers"

    answer_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.assessment_id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.question_id", ondelete="CASCADE"), nullable=False, index=True)
    answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    marks_awarded = Column(Float, default=0.0, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    student = relationship("Student", back_populates="answers")
    assessment = relationship("Assessment", back_populates="student_answers")
    question = relationship("Question", back_populates="student_answers")


class Result(Base):
    __tablename__ = "results"

    result_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.assessment_id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)
    passed = Column(Boolean, default=False, nullable=False)
    feedback = Column(Text, nullable=True)
    completed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    student = relationship("Student", back_populates="results")
    assessment = relationship("Assessment", back_populates="results")
