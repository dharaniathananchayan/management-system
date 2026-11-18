import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "ArchintX Learning Progress & Assessment Management System"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Advanced Learning Progress, Assessment & Performance Analytics Backend for ArchintX"
    
    # Database configuration (defaults to local SQLite, easily overridden with PostgreSQL/MySQL in .env)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./archintx.db")
    
    # JWT & Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "archintx-super-secret-key-change-in-production-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Inactivity threshold in days
    INACTIVE_THRESHOLD_DAYS: int = 7
    LOW_SCORE_THRESHOLD: float = 60.0  # Percentage below which student is flagged as needing support

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
