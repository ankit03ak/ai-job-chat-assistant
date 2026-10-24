import json
from collections.abc import Iterable
from pathlib import Path

from app.scrapers.base import SourceResult, deduplicate_jobs
from app.scrapers.greenhouse import GreenhouseAdapter
from app.scrapers.lever import LeverAdapter


def load_adapters(path: str | Path) -> list[GreenhouseAdapter | LeverAdapter]:
    configuration = json.loads(Path(path).read_text(encoding="utf-8"))
    adapters: list[GreenhouseAdapter | LeverAdapter] = []
    for source in configuration.get("greenhouse", []):
        if source.get("enabled", True):
            adapters.append(GreenhouseAdapter(source["company"], source["token"]))
    for source in configuration.get("lever", []):
        if source.get("enabled", True):
            adapters.append(LeverAdapter(source["company"], source["token"]))
    return adapters


def collect_sources(
    adapters: Iterable[object], *, max_records: int | None = None
) -> tuple[list, dict[str, SourceResult], int]:
    all_records = []
    results: dict[str, SourceResult] = {}
    for adapter in adapters:
        result = adapter.fetch(limit=max_records)
        results[result.source_name] = result
        all_records.extend(result.records)
    records, duplicate_count = deduplicate_jobs(all_records)
    if max_records is not None:
        records = records[:max_records]
    return records, results, duplicate_count
