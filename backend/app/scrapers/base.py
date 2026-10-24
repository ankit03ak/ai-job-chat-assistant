from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Protocol
from urllib.parse import urlsplit, urlunsplit

from app.schemas.job import Job


@dataclass
class SourceResult:
    source_name: str
    records: list[Job] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class JobSourceAdapter(Protocol):
    name: str

    def fetch(self, *, limit: int | None = None) -> SourceResult:
        """Fetch only from a source that has been verified as permitted."""


def canonicalize_url(value: str) -> str:
    parsed = urlsplit(value.strip())
    host = parsed.netloc.casefold()
    path = parsed.path.rstrip("/")
    return urlunsplit((parsed.scheme.casefold(), host, path, parsed.query, ""))


def normalize_text(value: str) -> str:
    return " ".join(value.casefold().split())


def job_fingerprint(job: Job) -> str:
    value = "|".join(
        (
            normalize_text(job.title),
            normalize_text(job.company),
            normalize_text(job.location),
        )
    )
    return sha256(value.encode("utf-8")).hexdigest()


def deduplicate_jobs(records: list[Job]) -> tuple[list[Job], int]:
    unique: list[Job] = []
    seen_urls: set[str] = set()
    seen_ids: set[str] = set()
    seen_fingerprints: set[str] = set()
    duplicates = 0
    for job in records:
        source_url = canonicalize_url(str(job.source_url))
        fingerprint = job_fingerprint(job)
        if source_url in seen_urls or job.job_id in seen_ids or fingerprint in seen_fingerprints:
            duplicates += 1
            continue
        seen_urls.add(source_url)
        seen_ids.add(job.job_id)
        seen_fingerprints.add(fingerprint)
        unique.append(job)
    return unique, duplicates


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
