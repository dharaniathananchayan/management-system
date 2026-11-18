from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Course(Base):
    __tablename__ = "courses"

    course_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_name = Column(String(150), nullable=False, index=True)
    category = Column(String(80), default="Python & Backend", nullable=True)
    level = Column(String(50), default="Beginner", nullable=True)  # Beginner, Intermediate, Advanced
    duration_hours = Column(Integer, default=20, nullable=True)
    passing_criteria = Column(Integer, default=60, nullable=True)
    instructor_name = Column(String(120), default="Senior Faculty", nullable=True)
    prerequisites = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(30), default="Active", nullable=False)  # Active, Draft, Archived
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan", order_by="Module.order_index")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="course", cascade="all, delete-orphan")


class Module(Base):
    __tablename__ = "modules"

    module_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False, index=True)
    module_name = Column(String(150), nullable=False)
    order_index = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan", order_by="Lesson.order_index")
    questions = relationship("Question", back_populates="module", cascade="all, delete-orphan")


class Lesson(Base):
    __tablename__ = "lessons"

    lesson_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    module_id = Column(Integer, ForeignKey("modules.module_id", ondelete="CASCADE"), nullable=False, index=True)
    lesson_title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)
    duration_minutes = Column(Integer, default=15, nullable=False)
    order_index = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    module = relationship("Module", back_populates="lessons")
    progress_records = relationship("Progress", back_populates="lesson", cascade="all, delete-orphan")
