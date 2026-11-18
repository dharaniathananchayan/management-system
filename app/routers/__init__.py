from app.routers.auth import router as auth_router
from app.routers.students import router as students_router
from app.routers.courses import router as courses_router
from app.routers.assessments import router as assessments_router
from app.routers.progress import router as progress_router
from app.routers.analytics import router as analytics_router

__all__ = [
    "auth_router",
    "students_router",
    "courses_router",
    "assessments_router",
    "progress_router",
    "analytics_router",
]
