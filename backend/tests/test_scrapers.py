from datetime import datetime, timezone

from app.schemas.job import Job
from app.scrapers.base import canonicalize_url, deduplicate_jobs


def make_job(job_id: str, url: str, title: str = "Engineer") -> Job:
    return Job(
        job_id=job_id,
        title=title,
        company="Example",
        location="Remote",
        work_mode="remote",
        skills=[],
        description="A verified fixture",
        source_name="Test source",
        source_url=url,
        scraped_at=datetime.now(timezone.utc),
    )


def test_url_canonicalization_removes_case_and_trailing_slash():
    assert canonicalize_url("HTTPS://Example.com/jobs/1/") == "https://example.com/jobs/1"


def test_deduplication_uses_url_then_id_then_fingerprint():
    records, duplicates = deduplicate_jobs(
        [
            make_job("one", "https://example.com/1"),
            make_job("two", "https://example.com/1"),
            make_job("one", "https://example.com/2"),
            make_job("three", "https://example.com/3"),
        ]
    )
    assert len(records) == 1
    assert duplicates == 3
