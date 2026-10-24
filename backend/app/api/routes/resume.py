from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.config import get_settings
from app.schemas.resume import ResumeParseResponse
from app.services.resume_parser import ResumeParseError, extract_resume_text
from app.services.resume_service import ResumeProfileError, ResumeProfileService

router = APIRouter(prefix="/api/v1/resume", tags=["resume"])


@router.post("/parse", response_model=ResumeParseResponse)
async def parse_resume(file: UploadFile = File(...)) -> ResumeParseResponse:
    settings = get_settings()
    content = await file.read()
    try:
        text = extract_resume_text(content, file.filename or "", settings.max_upload_mb)
        profile = ResumeProfileService(settings.gemini_api_key, settings.gemini_model).extract_profile(text)
    except ResumeParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ResumeProfileError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return ResumeParseResponse(profile=profile, warnings=profile.warnings)
