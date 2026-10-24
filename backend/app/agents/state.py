from typing import TypedDict

from app.schemas.application import ApplicationResponse
from app.schemas.chat import ChatResponse
from app.schemas.matching import JobMatch
from app.schemas.resume import ResumeProfile


class SearchFilters(TypedDict, total=False):
    q: str
    skill: str
    location: str
    work_mode: str
    experience: str
    employment_type: str


class AgentState(TypedDict, total=False):
    message: str
    resume_profile: ResumeProfile | None
    visible_job_ids: list[str]
    visible_job_offset: int
    intent: str
    search_filters: SearchFilters
    technical_only: bool
    matched_jobs: list[JobMatch]
    selected_job_id: str | None
    application_result: ApplicationResponse | None
    applications: list[ApplicationResponse]
    reply: str
    errors: list[str]
    response: ChatResponse
