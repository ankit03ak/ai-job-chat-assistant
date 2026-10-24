from pydantic import BaseModel, Field


class EducationItem(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    graduation_year: int | None = None


class ProjectItem(BaseModel):
    name: str
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)


class ResumeProfile(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    current_designation: str | None = None
    target_designations: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    experience_summary: str | None = None
    total_experience_years: float | None = Field(default=None, ge=0)
    education: list[EducationItem] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)
    raw_text_available: bool = False
    warnings: list[str] = Field(default_factory=list)


class ResumeParseResponse(BaseModel):
    profile: ResumeProfile
    warnings: list[str] = Field(default_factory=list)
