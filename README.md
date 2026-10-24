# Hidani AI Job Chat Assistant

An AI-assisted job discovery application for the Hidani Tech SDE Intern
assessment. A user uploads a PDF or DOCX resume, receives a structured profile,
searches and ranks jobs conversationally, records simulated applications, and
reviews application history.

## Current scope

The application is intentionally safe: applications are recorded locally and
are never submitted to employers. The checked-in dataset contains 1,967 normalized public listings collected from
enabled Greenhouse and Lever job boards. The source configuration and collection
scripts preserve source URLs and provenance fields. Listings are used for job
discovery only; applications remain simulated and are never submitted to
employers.

## Architecture and dataflow

1. Next.js sends resume files and chat requests to the FastAPI API.
2. FastAPI extracts PDF/DOCX text locally.
3. Gemini produces a structured `ResumeProfile`; the raw resume file is not
   persisted.
4. The LangGraph orchestrator classifies the request and calls search,
   matching, application, or tracking tools.
5. `JobRepository` validates and searches the JSON dataset.
6. `JobMatcher` scores skills, designation, experience, and remote work.
7. SQLAlchemy persists simulated applications in SQLite with a unique job ID
   constraint.
8. The Next.js UI renders the conversation, profile, ranked jobs, and
   application history.

## Local setup

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload
```

Set `GEMINI_API_KEY` and `GEMINI_MODEL` in `backend/.env` to enable resume
profile extraction. `FRONTEND_ORIGINS` must contain the frontend origin.

### Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

Set `NEXT_PUBLIC_API_BASE_URL` to the FastAPI origin.

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/jobs` | Filtered, paginated job listings |
| GET | `/api/v1/jobs/{job_id}` | Read one job |
| POST | `/api/v1/resume/parse` | Parse PDF/DOCX into a structured profile |
| POST | `/api/v1/chat` | Search, apply, and track through the assistant |
| POST | `/api/v1/applications` | Record a simulated application |
| GET | `/api/v1/applications` | List recorded applications |
| GET | `/api/v1/applications/{id}` | Read one application |

## Dataset collection

The collector is at `backend/scripts/scrape_jobs.py`. It loads enabled public
Greenhouse and Lever boards from `backend/data/job_sources.json`, applies
deduplication, and writes atomically. Run these commands from the repository
root:

```powershell
cd backend
python scripts/validate_jobs.py
python scripts/scrape_jobs.py --dry-run --max-records 2000
```

To discover currently active boards and rebuild the source configuration:

```powershell
cd backend
python scripts/build_sources.py
python scripts/trim_sources.py
python scripts/scrape_jobs.py --max-records 2000
python scripts/validate_jobs.py
```

The `build_sources.py` script uses the `requests` dependency and checks the
public board endpoints. `trim_sources.py` keeps the selected boards enabled.
Review `data/job_sources.json` before collecting. Never bypass a platform's
terms, authentication, or rate limits.

## Validation

```powershell
cd backend
python -m pytest
cd ..\frontend
npm run typecheck
npm run build
```

## Assignment submission checklist

- [ ] Deploy frontend and backend and verify the live end-to-end flow.
- [ ] Configure production CORS and `NEXT_PUBLIC_API_BASE_URL`.
- [x] Add a permitted real 1,500-2,000 listing dataset.
- [x] Include the scraper adapters and provenance fields.
- [ ] Record a 3-5 minute demo: upload, parse, search, refine, apply, and track.
- [ ] Publish this repository and include the live URL in the submission.
