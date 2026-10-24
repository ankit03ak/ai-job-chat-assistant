import json
from pathlib import Path
from threading import Lock

from pydantic import TypeAdapter, ValidationError

from app.schemas.job import Job


class JobDataError(RuntimeError):
    """Raised when the job dataset cannot be loaded or validated."""


class JobRepository:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._jobs: list[Job] | None = None
        self._loaded_mtime_ns: int | None = None
        self._lock = Lock()

    def _load(self) -> list[Job]:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            jobs = TypeAdapter(list[Job]).validate_python(raw)
        except FileNotFoundError as exc:
            raise JobDataError(f"Job dataset not found: {self.path}") from exc
        except (OSError, json.JSONDecodeError, ValidationError) as exc:
            raise JobDataError(f"Job dataset is invalid: {self.path}") from exc

        job_ids = [job.job_id for job in jobs]
        if len(job_ids) != len(set(job_ids)):
            raise JobDataError("Job dataset contains duplicate job_id values")
        return jobs

    def _ensure_loaded(self) -> list[Job]:
        with self._lock:
            current_mtime_ns = self.path.stat().st_mtime_ns
            if self._jobs is None or current_mtime_ns != self._loaded_mtime_ns:
                self._jobs = self._load()
                self._loaded_mtime_ns = current_mtime_ns
            return self._jobs

    def reload(self) -> None:
        with self._lock:
            self._jobs = self._load()
            self._loaded_mtime_ns = self.path.stat().st_mtime_ns

    def list(
        self,
        *,
        q: str | None = None,
        skill: str | None = None,
        location: str | None = None,
        work_mode: str | None = None,
        experience: str | None = None,
        employment_type: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Job], int]:
        jobs = self._ensure_loaded()
        terms = q.casefold() if q else None
        filtered = [
            job
            for job in jobs
            if (not terms or terms in f"{job.title} {job.company} {job.description}".casefold())
            and (not skill or any(skill.casefold() in item.casefold() for item in job.skills))
            and (not location or location.casefold() in job.location.casefold())
            and (not work_mode or work_mode.casefold() == job.work_mode.casefold())
            and (not experience or experience.casefold() in (job.experience_required or "").casefold())
            and (
                not employment_type
                or employment_type.casefold() == (job.employment_type or "").casefold()
            )
        ]
        start = (page - 1) * page_size
        return filtered[start : start + page_size], len(filtered)

    def get(self, job_id: str) -> Job | None:
        return next((job for job in self._ensure_loaded() if job.job_id == job_id), None)
