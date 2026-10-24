from collections.abc import Iterable

from app.scrapers.base import SourceResult, deduplicate_jobs


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
