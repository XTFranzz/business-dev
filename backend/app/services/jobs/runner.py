import uuid
from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.models import SearchJob, SearchResult
from app.models.enums import SearchJobStatus
from app.services.dedup.matcher import find_existing_business
from app.services.jobs.ingest import create_business_from_discovery
from app.services.providers.base import DiscoveryParams
from app.services.providers.registry import get_discovery_provider


async def run_search_job(job_id: uuid.UUID) -> None:
    db = SessionLocal()
    try:
        job = db.get(SearchJob, job_id)
        if job is None:
            return

        job.status = SearchJobStatus.RUNNING
        job.started_at = datetime.now(timezone.utc)
        db.commit()

        params = DiscoveryParams(**job.params)
        provider = get_discovery_provider()

        try:
            discovered_list = await provider.search(params)
        except Exception as exc:  # noqa: BLE001 - persisted as the job's own failure state
            job.status = SearchJobStatus.FAILED
            job.error = str(exc)
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
            return

        job.found_count = len(discovered_list)
        db.commit()

        for discovered in discovered_list:
            business = find_existing_business(db, discovered)
            if business is None:
                business = create_business_from_discovery(db, discovered)

            db.add(
                SearchResult(
                    job_id=job.id,
                    business_id=business.id,
                    raw_provider_payload=discovered.raw_payload,
                )
            )
            job.processed_count += 1
            db.commit()

        job.status = SearchJobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()
