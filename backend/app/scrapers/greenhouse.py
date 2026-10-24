import json
from dataclasses import dataclass

from app.schemas.job import Job
from app.scrapers.base import SourceResult, now_utc
from app.scrapers.common import (
    clean_html,
    infer_experience,
    infer_skills,
    infer_work_mode,
    parse_datetime,
)
from app.scrapers.http import SourceFetchError, fetch_json


@dataclass(frozen=True)
class GreenhouseAdapter:
    company: str
    board_token: str
    timeout: float = 15

    @property
    def name(self) -> str:
        return f"Greenhouse:{self.company}"

    def fetch(self, *, limit: int | None = None) -> SourceResult:
        url = f"https://boards-api.greenhouse.io/v1/boards/{self.board_token}/jobs?content=true"
        try:
            payload = json.loads(fetch_json(url, timeout=self.timeout))
            jobs = payload.get("jobs", [])
            records = [self._to_job(item) for item in jobs[:limit] if self._is_valid(item)]
            return SourceResult(source_name=self.name, records=records)
        except (SourceFetchError, json.JSONDecodeError, TypeError, ValueError) as exc:
            return SourceResult(source_name=self.name, errors=[str(exc)])

    def _to_job(self, item: dict) -> Job:
        location = item.get("location", {}).get("name") or "Unspecified"
        description = clean_html(item.get("content")) or item["title"]
        text = f"{item['title']} {description}"
        return Job(
            job_id=f"greenhouse-{self.board_token}-{item['id']}",
            title=item["title"],
            company=self.company,
            location=location,
            work_mode=infer_work_mode(f"{location} {text}"),
            experience_required=infer_experience(text),
            skills=infer_skills(text),
            description=description,
            source_name="Greenhouse",
            source_url=item["absolute_url"],
            posted_at=parse_datetime(item.get("updated_at")),
            employment_type=None,
            salary=None,
            scraped_at=now_utc(),
        )

    @staticmethod
    def _is_valid(item: object) -> bool:
        return (
            isinstance(item, dict)
            and isinstance(item.get("id"), int)
            and bool(item.get("title"))
            and bool(item.get("absolute_url"))
        )
