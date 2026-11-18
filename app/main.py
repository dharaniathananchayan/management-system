from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.config import settings
from app.database import engine, Base
from app.routers import (
    auth_router,
    students_router,
    courses_router,
    assessments_router,
    progress_router,
    analytics_router,
)

# Auto-create all tables in database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Enable CORS for flexible integration with ArchintX platform frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates & Static directory setup
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Mount static files
static_dir = BASE_DIR / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Register API Routers
app.include_router(auth_router)
app.include_router(students_router)
app.include_router(courses_router)
app.include_router(assessments_router)
app.include_router(progress_router)
app.include_router(analytics_router)


# Root endpoint - Serves the interactive ArchintX demo dashboard
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index_view(request: Request):
    """Serve the ArchintX interactive system dashboard matching the specification mockups."""
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/health", tags=["System"])
def health_check():
    """System health & readiness check."""
    return {
        "status": "healthy",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


# Global Exception Handler for database integrity and general exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    trace = traceback.format_exc()
    # In production/debug return JSON structure
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred.", "error": str(exc)},
    )
