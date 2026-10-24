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

The checked-in `data/jobs.json` contains the collected normalized dataset.
Tests use temporary synthetic fixtures and do not modify the production dataset.

## Dataset and collection scripts

Validate the production dataset:

```powershell
python scripts/validate_jobs.py
```

Review the enabled public Greenhouse and Lever boards in
`data/job_sources.json`, then run the collector in dry-run mode:

```powershell
python scripts/scrape_jobs.py --dry-run --max-records 2000
```

The collector includes public Greenhouse and Lever adapters. Non-dry-run
collection refuses to overwrite `data/jobs.json` when no adapter is configured.
Collection uses provenance, canonical URL/job-id/fingerprint deduplication,
bounded retries, rate-limit errors, maximum-record limits, and atomic writes.
The Lever iframe embed is not the data endpoint; use the corresponding
`https://api.lever.co/v0/postings/{token}?mode=json` endpoint.

For Greenhouse, use the board token from the careers URL. Greenhouse content is
cleaned from HTML and the original `absolute_url` is preserved as `source_url`.

The helper scripts are safe to run from any working directory:

```powershell
cd backend
python scripts/build_sources.py
python scripts/trim_sources.py
python scripts/scrape_jobs.py --dry-run --max-records 2000
python scripts/scrape_jobs.py --max-records 2000
python scripts/validate_jobs.py
```

Synthetic fixtures are always written separately:

```powershell
python scripts/seed_demo_jobs.py
python scripts/validate_jobs.py --path data/demo_jobs.json
```

`demo_jobs.json` is not a real job dataset and must not be merged into
`data/jobs.json`.
