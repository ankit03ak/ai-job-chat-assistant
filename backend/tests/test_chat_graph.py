import json
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agents.graph import run_chat
from app.db.database import Base
from app.repositories.job_repository import JobRepository
from app.schemas.resume import ResumeProfile


def test_graph_searches_and_keeps_stable_conversation_id(tmp_path):
    dataset = tmp_path / "jobs.json"
    dataset.write_text(
        json.dumps(
            [
                {
                    "job_id": "job-1",
                    "title": "Python Developer",
                    "company": "Example",
                    "location": "Remote",
                    "work_mode": "remote",
                    "skills": ["Python"],
                    "description": "Build APIs",
                    "source_name": "Test",
                    "source_url": "https://example.com/job-1",
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                }
            ]
        ),
        encoding="utf-8",
    )
    repository = JobRepository(dataset)
    engine = create_engine(f"sqlite:///{tmp_path / 'app.db'}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    profile = ResumeProfile(skills=["Python"])

    response = run_chat(
        repository,
        factory,
        message="Show remote Python jobs",
        conversation_id="conversation-1",
        resume_profile=profile,
        visible_job_ids=[],
    )

    assert response.conversation_id == "conversation-1"
    assert response.intent == "job_search"
    assert response.jobs[0].job.job_id == "job-1"


def test_graph_returns_resume_matches_for_automatic_recommendation_request(tmp_path):
    dataset = tmp_path / "jobs.json"
    dataset.write_text(
        json.dumps(
            [
                {
                    "job_id": "job-1",
                    "title": "Python Developer",
                    "company": "Example",
                    "location": "Remote",
                    "work_mode": "remote",
                    "skills": ["Python"],
                    "description": "Build APIs",
                    "source_name": "Test",
                    "source_url": "https://example.com/job-1",
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "job_id": "job-2",
                    "title": "Content Editor",
                    "company": "Example",
                    "location": "Remote",
                    "work_mode": "remote",
                    "skills": [],
                    "description": "Edit documents",
                    "source_name": "Test",
                    "source_url": "https://example.com/job-2",
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                }
            ]
        ),
        encoding="utf-8",
    )
    repository = JobRepository(dataset)
    engine = create_engine(f"sqlite:///{tmp_path / 'app.db'}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    response = run_chat(
        repository,
        factory,
        message="Show matching jobs",
        conversation_id=None,
        resume_profile=ResumeProfile(skills=["Python"]),
        visible_job_ids=[],
    )

    assert response.intent == "job_search"
    assert [match.job.job_id for match in response.jobs] == ["job-1"]


def test_graph_requires_explicit_application_and_resolves_display_reference(tmp_path):
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
    repository = JobRepository(dataset)
    engine = create_engine(f"sqlite:///{tmp_path / 'app.db'}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    vague = run_chat(repository, factory, message="I like job 1", conversation_id=None, resume_profile=None, visible_job_ids=["job-1"])
    applied = run_chat(repository, factory, message="Apply to job 1", conversation_id=None, resume_profile=None, visible_job_ids=["job-1"])

    assert "explicit request" in vague.reply
    assert len(applied.applications) == 1
    assert applied.applications[0].job_id == "job-1"
    assert applied.reply.startswith("Recorded a simulated application")


def test_graph_resolves_absolute_job_number_on_later_page(tmp_path):
    dataset = tmp_path / "jobs.json"
    dataset.write_text(
        json.dumps(
            [
                {
                    "job_id": "job-51",
                    "title": "Engineer",
                    "company": "Example",
                    "location": "Remote",
                    "work_mode": "remote",
                    "skills": [],
                    "description": "Build software",
                    "source_name": "Test",
                    "source_url": "https://example.com/job-51",
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                }
            ]
        ),
        encoding="utf-8",
    )
    repository = JobRepository(dataset)
    engine = create_engine(f"sqlite:///{tmp_path / 'app.db'}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    response = run_chat(
        repository,
        factory,
        message="Apply to job 51",
        conversation_id=None,
        resume_profile=None,
        visible_job_ids=["job-51"],
        visible_job_offset=50,
    )

    assert response.reply.startswith("Recorded a simulated application")


def test_graph_tracks_application_history(tmp_path):
    dataset = tmp_path / "jobs.json"
    dataset.write_text("[]", encoding="utf-8")
    repository = JobRepository(dataset)
    engine = create_engine(f"sqlite:///{tmp_path / 'app.db'}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    response = run_chat(
        repository,
        factory,
        message="Show my applied jobs",
        conversation_id=None,
        resume_profile=None,
        visible_job_ids=[],
    )

    assert response.intent == "application_tracking"
    assert response.applications == []
    assert "locally recorded" in response.reply
