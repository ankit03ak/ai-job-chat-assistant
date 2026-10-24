# AI Job Assistant backend

## Local development

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run tests with:

```powershell
python -m pytest
```

The checked-in `data/jobs.json` is intentionally empty until permitted sources are
verified and listings are collected with provenance. Tests use temporary synthetic
fixtures and do not modify the production dataset.

## Dataset and collection scripts

Validate the production dataset:

```powershell
python scripts/validate_jobs.py
```

Run the collector in dry-run mode:

```powershell
python scripts/scrape_jobs.py --dry-run --max-records 2000
```

The collector has no source adapter registered by default. A source must be
verified as permitted before an adapter is added. Non-dry-run collection refuses
to overwrite `data/jobs.json` when no adapter is configured. Collection uses
provenance, canonical URL/job-id/fingerprint deduplication, bounded retries,
rate-limit errors, maximum-record limits, and atomic writes.

Synthetic fixtures are always written separately:

```powershell
python scripts/seed_demo_jobs.py
python scripts/validate_jobs.py --path data/demo_jobs.json
```

`demo_jobs.json` is not a real job dataset and must not be merged into
`data/jobs.json`.
