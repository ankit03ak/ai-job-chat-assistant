from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.graph import run_chat
from app.api.routes.applications import get_session
from app.repositories.job_repository import JobRepository
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


def get_repository() -> JobRepository:
    from app.main import job_repository

    return job_repository


@router.post("", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    session: Session = Depends(get_session),
    repository: JobRepository = Depends(get_repository),
) -> ChatResponse:
    return run_chat(
        repository,
        lambda: session,
        message=request.message,
        conversation_id=request.conversation_id,
        resume_profile=request.resume_profile,
        visible_job_ids=request.visible_job_ids,
        visible_job_offset=request.visible_job_offset,
    )
