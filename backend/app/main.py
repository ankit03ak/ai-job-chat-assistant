from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import applications, chat, health, jobs, resume
from app.config import get_settings
from app.db.database import Base, create_database_engine, create_session_factory
from app.logging_config import configure_logging
from app.repositories.job_repository import JobRepository

settings = get_settings()
configure_logging(settings.log_level)
engine = create_database_engine(settings.database_url)
session_factory = create_session_factory(engine)
job_repository = JobRepository(settings.job_data_path)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Path(settings.job_data_path).parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="AI Job Assistant API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_frontend_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(resume.router)
app.include_router(chat.router)
