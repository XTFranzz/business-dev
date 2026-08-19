import uuid
from dataclasses import asdict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import SearchJob
from app.schemas.discover import DiscoverJobCreate, DiscoverJobRead
from app.services.jobs.runner import run_search_job
from app.services.providers.base import DiscoveryParams
from app.services.providers.registry import (
    DISCOVERY_PROVIDERS,
    ProviderNotConfiguredError,
    get_discovery_provider,
)

router = APIRouter(prefix="/discover", tags=["discover"])


@router.get("/providers")
def list_providers() -> dict:
    return {"providers": list(DISCOVERY_PROVIDERS)}


@router.get("/test")
async def test_discovery(
    category: str = Query(..., description="e.g. 'coffee shops'"),
    country: str = Query(...),
    state: str | None = Query(None),
    city: str | None = Query(None),
    max_results: int = Query(10, ge=1, le=60),
    provider: str = Query("google_places"),
) -> dict:
    try:
        provider_instance = get_discovery_provider(provider)
    except ProviderNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    params = DiscoveryParams(
        country=country, state=state, city=city, category=category, max_results=max_results
    )
    businesses = await provider_instance.search(params)
    return {"count": len(businesses), "results": [asdict(b) for b in businesses]}


@router.post("/jobs", response_model=DiscoverJobRead, status_code=201)
def create_search_job(
    payload: DiscoverJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> SearchJob:
    try:
        get_discovery_provider(payload.provider)
    except ProviderNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    job = SearchJob(params=payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(run_search_job, job.id)
    return job


@router.get("/jobs/{job_id}", response_model=DiscoverJobRead)
def get_search_job(job_id: uuid.UUID, db: Session = Depends(get_db)) -> SearchJob:
    job = db.get(SearchJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
