from sqlalchemy.orm import Session

from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from app.schemas.application import ApplicationResponse


class UnknownJobError(RuntimeError):
    """Raised when an application references an unknown job."""


class ApplicationService:
    def __init__(self, jobs: JobRepository, session: Session) -> None:
        self.jobs = jobs
        self.repository = ApplicationRepository(session)

    def apply(self, job_id: str) -> ApplicationResponse:
        job = self.jobs.get(job_id)
        if job is None:
            raise UnknownJobError(job_id)
        application = self.repository.create(job_id=job.job_id, title=job.title, company=job.company)
        return ApplicationResponse.model_validate(application)

    def list(self) -> list[ApplicationResponse]:
        return [ApplicationResponse.model_validate(item) for item in self.repository.list()]

    def get(self, application_id: int) -> ApplicationResponse | None:
        application = self.repository.get(application_id)
        return ApplicationResponse.model_validate(application) if application else None
