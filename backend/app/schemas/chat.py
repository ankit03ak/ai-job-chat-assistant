from pydantic import BaseModel, Field

from app.schemas.application import ApplicationResponse
from app.schemas.job import Job
from app.schemas.matching import JobMatch
from app.schemas.resume import ResumeProfile


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: str | None = None
    resume_profile: ResumeProfile | None = None
    visible_job_ids: list[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    intent: str
    jobs: list[JobMatch] = Field(default_factory=list)
    resume_profile: ResumeProfile | None = None
    applications: list[ApplicationResponse] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
