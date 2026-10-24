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
class LeverAdapter:
    company: str
    site_token: str
    timeout: float = 15

    @property
    def name(self) -> str:
        return f"Lever:{self.company}"

    def fetch(self, *, limit: int | None = None) -> SourceResult:
        url = f"https://api.lever.co/v0/postings/{self.site_token}?mode=json"
        try:
            payload = json.loads(fetch_json(url, timeout=self.timeout))
            records = [self._to_job(item) for item in payload[:limit] if self._is_valid(item)]
            return SourceResult(source_name=self.name, records=records)
        except (SourceFetchError, json.JSONDecodeError, TypeError, ValueError) as exc:
            return SourceResult(source_name=self.name, errors=[str(exc)])

    def _to_job(self, item: dict) -> Job:
        categories = item.get("categories", {})
        location = categories.get("location") or ", ".join(categories.get("allLocations", [])) or "Unspecified"
        description = clean_html(item.get("descriptionPlain") or item.get("description"))
        text = f"{item['text']} {description}"
        return Job(
            job_id=f"lever-{self.site_token}-{item['id']}",
            title=item["text"],
            company=self.company,
            location=location,
            work_mode=infer_work_mode(f"{location} {text}"),
            experience_required=infer_experience(text),
            skills=infer_skills(text),
            description=description or item["text"],
            source_name="Lever",
            source_url=item["hostedUrl"],
            posted_at=parse_datetime(item.get("createdAt")),
            employment_type=categories.get("commitment"),
            salary=None,
            scraped_at=now_utc(),
        )

    @staticmethod
    def _is_valid(item: object) -> bool:
        return (
            isinstance(item, dict)
            and bool(item.get("id"))
            and bool(item.get("text"))
            and bool(item.get("hostedUrl"))
        )
