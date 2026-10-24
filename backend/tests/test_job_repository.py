import json
from datetime import datetime, timezone

import pytest

from app.repositories.job_repository import JobDataError, JobRepository


def job(job_id: str, **overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "job_id": job_id,
        "title": "Python Developer",
        "company": "Example Co",
        "location": "Bengaluru, India",
        "work_mode": "remote",
        "experience_required": "0-2 years",
        "skills": ["Python", "FastAPI"],
        "description": "Build APIs",
        "source_name": "Test source",
        "source_url": "https://example.com/jobs/1",
        "posted_at": None,
        "employment_type": "full-time",
        "salary": None,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }
    value.update(overrides)
    return value


def test_repository_filters_and_paginates(tmp_path):
    path = tmp_path / "jobs.json"
    path.write_text(json.dumps([job("one"), job("two", work_mode="hybrid")]), encoding="utf-8")
    repository = JobRepository(path)

    items, total = repository.list(work_mode="remote", page=1, page_size=1)

    assert total == 1
    assert [item.job_id for item in items] == ["one"]


def test_repository_rejects_duplicate_ids(tmp_path):
    path = tmp_path / "jobs.json"
    path.write_text(json.dumps([job("same"), job("same")]), encoding="utf-8")

    with pytest.raises(JobDataError, match="duplicate"):
        JobRepository(path).get("same")


def test_repository_reloads_when_dataset_changes(tmp_path):
    path = tmp_path / "jobs.json"
    path.write_text(json.dumps([job("one")]), encoding="utf-8")
    repository = JobRepository(path)
    assert repository.list(page=1, page_size=10)[1] == 1

    path.write_text(json.dumps([job("one"), job("two")]), encoding="utf-8")

    assert repository.list(page=1, page_size=10)[1] == 2
