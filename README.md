# Business Lead Finder & Outreach Automation

Discovers businesses that lack a proper website, scores them as web-development leads, and (in
later phases) manages personalized outreach. See `.claude/plans/` history or ask for the current
build plan for the full phased spec.

## Status

Phase 1 (Core MVP) — in progress. Currently scaffolded: backend skeleton, frontend skeleton with
routing/layout, and placeholder pages. No discovery, auth, or scoring logic yet.

## Stack

- **Frontend:** React + TypeScript + Vite + Tailwind + shadcn/ui, React Router, TanStack Query.
- **Backend:** Python + FastAPI, SQLAlchemy + Alembic.
- **Database / Auth:** Supabase (hosted Postgres + Supabase Auth).
- **Discovery provider:** Google Places API (New).

## Getting started

### Backend

```bash
cd backend
python -m venv .venv
./.venv/Scripts/activate   # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
cp .env.example .env       # fill in SUPABASE_* / DATABASE_URL / GOOGLE_PLACES_API_KEY
uvicorn app.main:app --reload --port 8000
```

Health check: `GET http://localhost:8000/api/v1/health`. API docs: `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env        # fill in VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY
npm run dev
```

App: `http://localhost:5173`.

## Required external accounts

Nothing runs against real data until you provide:

1. A **Supabase** project (URL + anon key + service role key + JWT secret) — used for auth and as
   the Postgres database.
2. A **Google Cloud** project with the Places API (New) enabled and billing set up, plus its API
   key — used for business discovery.

Until these are supplied, the backend/frontend still build and run, but discovery/auth endpoints
will error clearly rather than return faked data.
