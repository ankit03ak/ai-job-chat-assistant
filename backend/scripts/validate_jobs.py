import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from pydantic import TypeAdapter, ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.schemas.job import Job  # noqa: E402


def validate_dataset(path: Path) -> tuple[int, dict[str, int]]:
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
        jobs = TypeAdapter(list[Job]).validate_python(records)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        raise ValueError(f"Invalid job dataset: {path}") from exc
    ids = [job.job_id for job in jobs]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate job_id values found")
    return len(jobs), dict(Counter(job.source_name for job in jobs))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, default=ROOT / "data" / "jobs.json")
    args = parser.parse_args()
    try:
        count, sources = validate_dataset(args.path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Validated {count} job record(s)")
    for source, source_count in sorted(sources.items()):
        print(f"- {source}: {source_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
