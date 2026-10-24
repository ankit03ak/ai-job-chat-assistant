from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.repositories.application_repository import DuplicateApplicationError
from app.repositories.job_repository import JobRepository
from app.schemas.application import ApplicationCreate, ApplicationResponse
from app.services.application_service import ApplicationService, UnknownJobError

router = APIRouter(prefix="/api/v1/applications", tags=["applications"])


def get_session() -> Session:
    from app.main import session_factory

    yield from get_db_session(session_factory)


def get_service(session: Session = Depends(get_session)) -> ApplicationService:
    from app.main import job_repository

    return ApplicationService(job_repository, session)


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    request: ApplicationCreate, service: ApplicationService = Depends(get_service)
) -> ApplicationResponse:
    try:
        return service.apply(request.job_id)
    except UnknownJobError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
    except DuplicateApplicationError as exc:
        raise HTTPException(status_code=409, detail="You have already applied to this job") from exc


@router.get("", response_model=list[ApplicationResponse])
def list_applications(service: ApplicationService = Depends(get_service)) -> list[ApplicationResponse]:
    return service.list()


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: int, service: ApplicationService = Depends(get_service)
) -> ApplicationResponse:
    application = service.get(application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return application
