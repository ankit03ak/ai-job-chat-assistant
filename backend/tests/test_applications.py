import json
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.repositories.application_repository import DuplicateApplicationError
from app.repositories.job_repository import JobRepository
from app.services.application_service import ApplicationService, UnknownJobError


def test_application_creation_and_duplicate_protection(tmp_path):
    dataset = tmp_path / "jobs.json"
    dataset.write_text(
        json.dumps(
            [
                {
                    "job_id": "job-1",
                    "title": "Engineer",
                    "company": "Example",
                    "location": "Remote",
                    "work_mode": "remote",
                    "skills": [],
                    "description": "Build software",
                    "source_name": "Test",
                    "source_url": "https://example.com/job-1",
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                }
            ]
        ),
        encoding="utf-8",
    )
    engine = create_engine(f"sqlite:///{tmp_path / 'app.db'}")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    service = ApplicationService(JobRepository(dataset), session_factory())

    created = service.apply("job-1")
    assert created.status == "simulated_applied"
    with pytest.raises(DuplicateApplicationError):
        service.apply("job-1")
    with pytest.raises(UnknownJobError):
        service.apply("missing")
