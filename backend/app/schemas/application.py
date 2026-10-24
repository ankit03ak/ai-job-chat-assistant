from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApplicationCreate(BaseModel):
    job_id: str


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: str
    job_title_snapshot: str
    company_snapshot: str
    applied_at: datetime
    status: str
    application_method: str
    notes: str | None = None
