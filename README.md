# Business Lead Finder & Outreach Automation

Discovers businesses that lack a proper website, scores them as web-development leads, and (in
later phases) manages personalized outreach. Single-user tool — no login/auth by design, not meant
to be exposed on the public internet.

## Status

Phase 1 (Core MVP) — in progress. Currently scaffolded: backend skeleton with database schema,
frontend skeleton with routing/layout and placeholder pages, and a working Google Places (New)
connection. No discovery pipeline or scoring logic yet.

## Stack

- **Frontend:** React + TypeScript + Vite + Tailwind + shadcn/ui, React Router, TanStack Query.
- **Backend:** Python + FastAPI, SQLAlchemy + Alembic.
- **Database:** Supabase Postgres (used purely as a hosted Postgres instance — no Supabase Auth).
- **Discovery provider:** Google Places API (New).

## Getting started

### Backend

```bash
cd backend
python -m venv .venv
./.venv/Scripts/activate   # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
cp .env.example .env       # fill in DATABASE_URL / GOOGLE_PLACES_API_KEY
alembic upgrade head       # applies the schema to your database
uvicorn app.main:app --reload --port 8000
```

Health check: `GET http://localhost:8000/api/v1/health`. API docs: `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env        # VITE_API_BASE_URL defaults to http://localhost:8000/api/v1
npm run dev
```

App: `http://localhost:5173`.

## Required external accounts

Nothing runs against real data until you provide:

1. A **Postgres database** — currently a Supabase project's connection string, used only as a
   hosted Postgres instance (no Supabase Auth involved).
2. A **Google Cloud** project with the Places API (New) enabled, plus its API key — used for
   business discovery.

Until these are supplied, the backend/frontend still build and run, but discovery endpoints will
error clearly rather than return faked data.
