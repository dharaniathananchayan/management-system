from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentLogin, StudentOut, Token
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_student,
)
from app.config import settings

router = APIRouter(tags=["Student Authentication"])


@router.post("/students/register", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
def register_student(payload: StudentCreate, db: Session = Depends(get_db)):
    """
    Register a new student account.
    - Validates email uniqueness
    - Securely hashes password using bcrypt
    - Returns registered student profile
    """
    existing = db.query(Student).filter(Student.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A student with this email address already exists.",
        )

    student = Student(
        name=payload.name.strip(),
        email=payload.email.lower().strip(),
        password_hash=hash_password(payload.password),
        role=payload.role if payload.role in ["student", "admin", "instructor"] else "student",
        is_active=True,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.post("/students/login", response_model=Token)
def login_student(payload: StudentLogin, db: Session = Depends(get_db)):
    """
    Authenticate student and return JWT access token.
    Accepts standard JSON body with email and password.
    """
    student = db.query(Student).filter(Student.email == payload.email.lower()).first()
    if not student or not verify_password(payload.password, student.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not student.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated. Please contact support.",
        )

    token = create_access_token(
        data={"sub": str(student.student_id), "email": student.email, "role": student.role}
    )
    return Token(access_token=token, token_type="bearer", student=student)


@router.post("/token", response_model=Token, include_in_schema=False)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 password form compatible endpoint for Swagger UI Authorize dialog."""
    student = db.query(Student).filter(Student.email == form_data.username.lower()).first()
    if not student or not verify_password(form_data.password, student.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username (email) or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(
        data={"sub": str(student.student_id), "email": student.email, "role": student.role}
    )
    return Token(access_token=token, token_type="bearer", student=student)


@router.get("/students/me", response_model=StudentOut)
def get_current_student_profile(current_student: Student = Depends(get_current_student)):
    """Get profile of currently logged-in student."""
    return current_student
