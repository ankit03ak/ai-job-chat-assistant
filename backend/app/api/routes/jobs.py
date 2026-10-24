from fastapi import APIRouter, Depends, HTTPException, Query

from app.repositories.job_repository import JobDataError, JobRepository
from app.schemas.job import Job, JobListResponse

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


def get_job_repository() -> JobRepository:
    from app.main import job_repository

    return job_repository


@router.get("", response_model=JobListResponse)
def list_jobs(
    repository: JobRepository = Depends(get_job_repository),
    q: str | None = None,
    skill: str | None = None,
    location: str | None = None,
    work_mode: str | None = None,
    experience: str | None = None,
    employment_type: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> JobListResponse:
    try:
        items, total = repository.list(
            q=q,
            skill=skill,
            location=location,
            work_mode=work_mode,
            experience=experience,
            employment_type=employment_type,
            page=page,
            page_size=page_size,
        )
    except JobDataError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return JobListResponse(items=items, page=page, page_size=page_size, total=total)


@router.get("/{job_id}", response_model=Job)
def get_job(job_id: str, repository: JobRepository = Depends(get_job_repository)) -> Job:
    try:
        job = repository.get(job_id)
    except JobDataError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
