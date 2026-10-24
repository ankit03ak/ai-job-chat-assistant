import argparse
import json
import logging
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.scrapers.registry import collect_sources, load_adapters  # noqa: E402

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect jobs from explicitly registered permitted adapters.")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "jobs.json")
    parser.add_argument("--sources", type=Path, default=ROOT / "data" / "job_sources.json")
    parser.add_argument("--max-records", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        adapters = load_adapters(args.sources)
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"Could not load source configuration: {exc}", file=sys.stderr)
        return 2
    records, results, duplicates = collect_sources(adapters, max_records=args.max_records)
    for source, result in results.items():
        for error in result.errors:
            logging.error("%s: %s", source, error)
    print(f"Collected {len(records)} unique record(s); removed {duplicates} duplicate(s)")
    if args.dry_run:
        return 0
    if not results:
        print(
            "No source adapters are registered. Refusing to overwrite the dataset "
            "until a permitted source is configured.",
            file=sys.stderr,
        )
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps([record.model_dump(mode="json") for record in records], indent=2) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=args.output.parent, delete=False) as temp:
        temp.write(payload)
        temporary_path = Path(temp.name)
    temporary_path.replace(args.output)
    print(f"Wrote dataset atomically to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
