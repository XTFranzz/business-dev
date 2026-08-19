from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Business, BusinessWebsite, LeadScore
from app.models.enums import BusinessStatus, WebsiteStatus
from app.schemas.dashboard import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

HIGH_OPPORTUNITY_THRESHOLD = 70


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)) -> DashboardStats:
    total_leads = db.execute(select(func.count()).select_from(Business)).scalar_one()

    new_leads = db.execute(
        select(func.count())
        .select_from(Business)
        .where(Business.status == BusinessStatus.NEW)
    ).scalar_one()

    no_website = db.execute(
        select(func.count(func.distinct(Business.id)))
        .select_from(Business)
        .join(BusinessWebsite, BusinessWebsite.business_id == Business.id)
        .where(BusinessWebsite.status == WebsiteStatus.NONE)
    ).scalar_one()

    high_opportunity = db.execute(
        select(func.count(func.distinct(Business.id)))
        .select_from(Business)
        .join(LeadScore, LeadScore.business_id == Business.id)
        .where(LeadScore.score >= HIGH_OPPORTUNITY_THRESHOLD)
    ).scalar_one()

    # Contacted/Replied/Interested/Converted require outreach tracking (Phase 3, not built yet).
    return DashboardStats(
        total_leads=total_leads,
        new_leads=new_leads,
        no_website=no_website,
        high_opportunity=high_opportunity,
        contacted=0,
        replied=0,
        interested=0,
        converted=0,
    )
