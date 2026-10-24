import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="Write clearly synthetic demo jobs to a separate file.")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "demo_jobs.json")
    args = parser.parse_args()
    now = datetime.now(timezone.utc).isoformat()
    records = [
        {
            "job_id": "demo-synthetic-001",
            "title": "Synthetic Python Engineer",
            "company": "Synthetic Demo Company",
            "location": "Remote",
            "work_mode": "remote",
            "experience_required": "0-2 years",
            "skills": ["Python", "FastAPI"],
            "description": "Synthetic fixture for local development only.",
            "source_name": "Synthetic demo fixture - not a real listing",
            "source_url": "https://example.invalid/demo/synthetic-python-engineer",
            "posted_at": None,
            "employment_type": "full-time",
            "salary": None,
            "scraped_at": now,
        }
    ]
    args.output.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(records)} synthetic demo record(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
