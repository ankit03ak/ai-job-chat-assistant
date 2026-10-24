from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Application


class DuplicateApplicationError(RuntimeError):
    """Raised when an application already exists for a job."""


class ApplicationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, *, job_id: str, title: str, company: str) -> Application:
        application = Application(job_id=job_id, job_title_snapshot=title, company_snapshot=company)
        self.session.add(application)
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise DuplicateApplicationError(job_id) from exc
        self.session.refresh(application)
        return application

    def list(self) -> list[Application]:
        return list(self.session.scalars(select(Application).order_by(Application.applied_at.desc())))

    def get(self, application_id: int) -> Application | None:
        return self.session.get(Application, application_id)
