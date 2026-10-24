import re

from sqlalchemy.orm import Session

from app.repositories.job_repository import JobRepository
from app.schemas.application import ApplicationResponse
from app.schemas.matching import JobMatch
from app.schemas.resume import ResumeProfile
from app.services.application_service import ApplicationService
from app.services.job_matcher import JobMatcher


TECHNICAL_ROLE_MARKERS = (
    "software",
    "frontend",
    "front-end",
    "backend",
    "back-end",
    "full stack",
    "full-stack",
    "developer",
    "development",
    "engineer",
    "engineering",
    "data",
    "machine learning",
    "artificial intelligence",
    "ai ",
    "devops",
    "cloud",
    "infrastructure",
    "platform",
    "site reliability",
    "sre",
    "qa",
    "quality assurance",
    "automation",
    "cyber",
    "security",
    "database",
    "network",
    "systems",
    "it support",
    "information technology",
    "technical support",
    "solutions architect",
    "architect",
    "product manager",
    "technical program",
    "ux",
    "ui",
    "designer",
)


def is_technical_job(job) -> bool:
    searchable = " ".join((job.title, job.description, *job.skills)).casefold()
    return any(marker in searchable for marker in TECHNICAL_ROLE_MARKERS)


def search_jobs(
    repository: JobRepository,
    filters: dict[str, str],
    profile: ResumeProfile | None,
    *,
    technical_only: bool = False,
) -> list[JobMatch]:
    jobs, _ = repository.list(**filters, page=1, page_size=10000)
    if technical_only:
        jobs = [job for job in jobs if is_technical_job(job)]
    if profile is None:
        return [
            JobMatch(job=job, match_score=0, match_reasons=["Upload a resume for personalized matching"])
            for job in jobs
        ]
    return JobMatcher().rank(profile, jobs)


def resolve_visible_job(
    message: str,
    visible_job_ids: list[str],
    repository: JobRepository,
    visible_job_offset: int = 0,
) -> str | None:
    match = re.search(r"\bjob\s*(?:number\s*)?(\d+)\b", message.casefold())
    if not match:
        return None
    position = int(match.group(1)) - 1 - visible_job_offset
    if 0 <= position < len(visible_job_ids):
        job_id = visible_job_ids[position]
        return job_id if repository.get(job_id) else None
    return None


def apply_to_job(repository: JobRepository, session: Session, job_id: str) -> ApplicationResponse:
    return ApplicationService(repository, session).apply(job_id)


def list_applications(repository: JobRepository, session: Session) -> list[ApplicationResponse]:
    return ApplicationService(repository, session).list()


def get_application_status(
    repository: JobRepository, session: Session, application_id: int
) -> ApplicationResponse | None:
    return ApplicationService(repository, session).get(application_id)
