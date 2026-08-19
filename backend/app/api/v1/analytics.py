from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Business, BusinessLocation, BusinessWebsite, Message
from app.models.enums import BusinessStatus, MessageStatus
from app.schemas.analytics import AnalyticsResponse, CountBucket

router = APIRouter(prefix="/analytics", tags=["analytics"])

TOP_N = 10


@router.get("", response_model=AnalyticsResponse)
def get_analytics(db: Session = Depends(get_db)) -> AnalyticsResponse:
    def _bucket(query) -> list[CountBucket]:
        return [
            CountBucket(
                label=(getattr(label, "value", label) if label else "Unknown"), count=count
            )
            for label, count in db.execute(query).all()
        ]

    business_count = func.count(func.distinct(BusinessLocation.business_id))

    by_country = _bucket(
        select(BusinessLocation.country, business_count)
        .group_by(BusinessLocation.country)
        .order_by(business_count.desc())
        .limit(TOP_N)
    )
    by_city = _bucket(
        select(BusinessLocation.city, business_count)
        .group_by(BusinessLocation.city)
        .order_by(business_count.desc())
        .limit(TOP_N)
    )
    by_category = _bucket(
        select(Business.category, func.count(Business.id))
        .group_by(Business.category)
        .order_by(func.count(Business.id).desc())
        .limit(TOP_N)
    )
    by_website_status = _bucket(
        select(
            BusinessWebsite.status, func.count(func.distinct(BusinessWebsite.business_id))
        ).group_by(BusinessWebsite.status)
    )
    by_status = _bucket(select(Business.status, func.count(Business.id)).group_by(Business.status))

    day = func.date_trunc("day", Business.discovered_at)
    leads_over_time_rows = db.execute(
        select(day, func.count(Business.id)).group_by(day).order_by(day)
    ).all()
    leads_over_time = [
        CountBucket(label=bucket_day.date().isoformat(), count=count)
        for bucket_day, count in leads_over_time_rows
    ]

    messages_sent = db.execute(
        select(func.count()).select_from(Message).where(Message.status == MessageStatus.SENT)
    ).scalar_one()
    messages_failed = db.execute(
        select(func.count()).select_from(Message).where(Message.status == MessageStatus.FAILED)
    ).scalar_one()
    replies = db.execute(
        select(func.count())
        .select_from(Business)
        .where(Business.status == BusinessStatus.REPLIED)
    ).scalar_one()

    return AnalyticsResponse(
        by_country=by_country,
        by_city=by_city,
        by_category=by_category,
        by_website_status=by_website_status,
        by_status=by_status,
        leads_over_time=leads_over_time,
        messages_sent=messages_sent,
        messages_failed=messages_failed,
        replies=replies,
    )
