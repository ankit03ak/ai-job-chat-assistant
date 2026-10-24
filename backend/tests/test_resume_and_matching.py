import json
from datetime import datetime, timezone

import pytest

from app.schemas.job import Job
from app.schemas.resume import ResumeProfile
from app.services.job_matcher import JobMatcher
from app.services.resume_parser import ResumeParseError, extract_resume_text


def test_invalid_resume_type_and_empty_content_are_rejected():
    with pytest.raises(ResumeParseError, match="Only PDF"):
        extract_resume_text(b"text", "resume.txt", 5)
    with pytest.raises(ResumeParseError, match="empty"):
        extract_resume_text(b"", "resume.pdf", 5)


def test_resume_size_limit_is_enforced():
    with pytest.raises(ResumeParseError, match="5 MB"):
        extract_resume_text(b"x" * (5 * 1024 * 1024 + 1), "resume.docx", 5)


def test_match_score_is_bounded_and_deterministic():
    job = Job(
        job_id="job-1",
        title="Python Developer",
        company="Example",
        location="Remote",
        work_mode="remote",
        skills=["Python", "FastAPI"],
        description="Build APIs",
        source_name="Test",
        source_url="https://example.com/job-1",
        scraped_at=datetime.now(timezone.utc),
    )
    profile = ResumeProfile(
        skills=["Python"],
        target_designations=["Python Developer"],
        total_experience_years=1,
    )
    matcher = JobMatcher()
    first = matcher.score(profile, job)
    second = matcher.score(profile, job)

    assert 0 <= first.match_score <= 100
    assert first == second
    assert first.matched_skills == ["Python"]
