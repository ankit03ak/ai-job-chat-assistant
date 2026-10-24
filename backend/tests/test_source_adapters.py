import json

from app.scrapers.greenhouse import GreenhouseAdapter
from app.scrapers.lever import LeverAdapter


def test_greenhouse_adapter_maps_public_job(monkeypatch):
    payload = {
        "jobs": [
            {
                "id": 127817,
                "title": "Python Engineer",
                "updated_at": "2026-01-14T10:55:28-05:00",
                "location": {"name": "Remote"},
                "absolute_url": "https://boards.greenhouse.io/example/jobs/127817",
                "content": "<p>Build Python APIs with FastAPI.</p>",
            }
        ]
    }
    monkeypatch.setattr(
        "app.scrapers.greenhouse.fetch_json",
        lambda *args, **kwargs: json.dumps(payload).encode(),
    )

    result = GreenhouseAdapter("Example", "example").fetch()

    assert len(result.records) == 1
    job = result.records[0]
    assert job.job_id == "greenhouse-example-127817"
    assert str(job.source_url) == "https://boards.greenhouse.io/example/jobs/127817"
    assert "Python" in job.skills
    assert job.work_mode == "remote"


def test_lever_adapter_maps_public_job(monkeypatch):
    payload = [
        {
            "id": "abc123",
            "text": "React Engineer",
            "createdAt": 1760000000000,
            "hostedUrl": "https://jobs.lever.co/example/abc123",
            "descriptionPlain": "Build React applications.",
            "categories": {
                "location": "New York",
                "commitment": "Full-time",
            },
        }
    ]
    monkeypatch.setattr(
        "app.scrapers.lever.fetch_json",
        lambda *args, **kwargs: json.dumps(payload).encode(),
    )

    result = LeverAdapter("Example", "example").fetch()

    assert len(result.records) == 1
    assert result.records[0].job_id == "lever-example-abc123"
    assert result.records[0].source_name == "Lever"
    assert "React" in result.records[0].skills
