from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class Job(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    company: str = Field(min_length=1)
    location: str = Field(min_length=1)
    work_mode: str = Field(min_length=1)
    experience_required: str | None = None
    skills: list[str] = Field(default_factory=list)
    description: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    source_url: HttpUrl
    posted_at: datetime | None = None
    employment_type: str | None = None
    salary: str | None = None
    scraped_at: datetime


class JobListResponse(BaseModel):
    items: list[Job]
    page: int
    page_size: int
    total: int
