import uuid
from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.models import LeadScore, SearchJob, SearchResult, WebsiteAnalysis
from app.models.enums import BusinessStatus, ContactType, SearchJobStatus, WebsiteStatus
from app.services.dedup.matcher import find_existing_business
from app.services.jobs.ingest import create_business_from_discovery
from app.services.lead_scoring.scorer import QUALIFY_THRESHOLD, ScoringInput, compute_lead_score
from app.services.providers.base import DiscoveryParams
from app.services.providers.registry import get_discovery_provider
from app.services.website_analysis.analyzer import analyze_website


async def run_search_job(job_id: uuid.UUID) -> None:
    db = SessionLocal()
    try:
        job = db.get(SearchJob, job_id)
        if job is None:
            return

        job.status = SearchJobStatus.RUNNING
        job.started_at = datetime.now(timezone.utc)
        db.commit()

        job_params = dict(job.params)
        provider_name = job_params.pop("provider", "google_places")
        params = DiscoveryParams(**job_params)
        provider = get_discovery_provider(provider_name)

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

            website = business.websites[0] if business.websites else None
            if website is not None and website.url and website.analysis is None:
                result = await analyze_website(website.url)
                website.status = result.status
                db.add(
                    WebsiteAnalysis(
                        website_id=website.id,
                        http_status=result.http_status,
                        https=result.https,
                        ssl_valid=result.ssl_valid,
                        final_redirect_url=result.final_redirect_url,
                        page_title=result.page_title,
                        meta_description=result.meta_description,
                        mobile_viewport_present=result.mobile_viewport_present,
                        load_time_ms=result.load_time_ms,
                        pages_crawled=result.pages_crawled,
                        has_contact_form=result.has_contact_form,
                        has_booking_form=result.has_booking_form,
                        broken_links_count=result.broken_links_count,
                        seo_score=result.seo_score,
                        quality_score=result.quality_score,
                    )
                )
                job.checked_count += 1
                db.flush()

            scoring_input = ScoringInput(
                has_website=bool(website and website.status not in (WebsiteStatus.NONE, None)),
                website_status=website.status if website else WebsiteStatus.NONE,
                website_quality_score=(
                    website.analysis.quality_score if website and website.analysis else None
                ),
                rating=business.rating,
                review_count=business.review_count,
                has_phone=any(c.type == ContactType.PHONE for c in business.contacts),
                has_email=any(c.type == ContactType.EMAIL for c in business.contacts),
                social_platform_count=len(business.socials),
            )
            score, reasons = compute_lead_score(scoring_input)

            if business.lead_score is None:
                business.lead_score = LeadScore(score=score, reasons=reasons)
            else:
                business.lead_score.score = score
                business.lead_score.reasons = reasons

            if score >= QUALIFY_THRESHOLD and business.status == BusinessStatus.NEW:
                business.status = BusinessStatus.QUALIFIED
                job.qualified_count += 1

            job.processed_count += 1
            db.commit()

        job.status = SearchJobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()
