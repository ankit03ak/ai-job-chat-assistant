from datetime import datetime, timezone

from app.agents.tools import is_technical_job
from app.schemas.job import Job


def make_job(title: str, description: str) -> Job:
    return Job(
        job_id=title.casefold().replace(" ", "-"),
        title=title,
        company="Example",
        location="Remote",
        work_mode="remote",
        description=description,
        source_name="Test",
        source_url=f"https://example.com/{title.casefold().replace(' ', '-')}",
        scraped_at=datetime.now(timezone.utc),
    )


def test_technical_relevance_includes_it_roles_and_excludes_nontechnical_roles():
    assert is_technical_job(make_job("Backend Software Engineer", "Build APIs")) is True
    assert is_technical_job(make_job("IT Support Specialist", "Support internal systems")) is True
    assert is_technical_job(make_job("Document Editor", "Edit written content")) is False
    assert is_technical_job(make_job("Typewriter", "Prepare typed documents")) is False
