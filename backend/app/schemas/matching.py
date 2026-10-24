from pydantic import BaseModel, Field

from app.schemas.job import Job


class JobMatch(BaseModel):
    job: Job
    match_score: float = Field(ge=0, le=100)
    matched_skills: list[str] = Field(default_factory=list)
    missing_or_unmatched_skills: list[str] = Field(default_factory=list)
    match_reasons: list[str] = Field(default_factory=list)
