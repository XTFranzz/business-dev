import csv
import io
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models import Business, BusinessWebsite, LeadScore, UnsubscribedEmail
from app.models.enums import BusinessStatus, ContactType, SocialPlatform
from app.schemas.business import (
    BusinessDetail,
    BusinessListItem,
    BusinessListResponse,
    BusinessStatusUpdate,
    ContactRead,
    LeadScoreRead,
    LocationRead,
    SocialRead,
    WebsiteRead,
)
from app.services.leads.query import build_filtered_leads_query

router = APIRouter(prefix="/leads", tags=["leads"])

_SORT_OPTIONS = {
    "discovered_at_desc": Business.discovered_at.desc(),
    "score_desc": LeadScore.score.desc(),
    "rating_desc": Business.rating.desc(),
    "reviews_desc": Business.review_count.desc(),
}


def _to_list_item(business: Business) -> BusinessListItem:
    location = business.locations[0] if business.locations else None
    website = business.websites[0] if business.websites else None
    has_phone = any(c.type == ContactType.PHONE for c in business.contacts)
    has_email = any(c.type == ContactType.EMAIL for c in business.contacts)

    return BusinessListItem(
        id=business.id,
        name=business.name,
        category=business.category,
        status=business.status,
        rating=business.rating,
        review_count=business.review_count,
        discovered_at=business.discovered_at,
        location=LocationRead.model_validate(location) if location else None,
        website=WebsiteRead.model_validate(website) if website else None,
        socials=[SocialRead.model_validate(s) for s in business.socials],
        has_phone=has_phone,
        has_email=has_email,
        lead_score=business.lead_score.score if business.lead_score else None,
    )


def _to_detail(business: Business) -> BusinessDetail:
    location = business.locations[0] if business.locations else None
    website = business.websites[0] if business.websites else None

    return BusinessDetail(
        id=business.id,
        name=business.name,
        category=business.category,
        description=business.description,
        status=business.status,
        source=business.source,
        source_url=business.source_url,
        rating=business.rating,
        review_count=business.review_count,
        discovered_at=business.discovered_at,
        location=LocationRead.model_validate(location) if location else None,
        website=WebsiteRead.model_validate(website) if website else None,
        socials=[SocialRead.model_validate(s) for s in business.socials],
        contacts=[ContactRead.model_validate(c) for c in business.contacts],
        lead_score=(
            LeadScoreRead.model_validate(business.lead_score) if business.lead_score else None
        ),
    )


@router.get("", response_model=BusinessListResponse)
def list_leads(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    search: str | None = Query(None),
    country: str | None = Query(None),
    state: str | None = Query(None),
    city: str | None = Query(None),
    category: str | None = Query(None),
    min_rating: float | None = Query(None, ge=0, le=5),
    min_reviews: int | None = Query(None, ge=0),
    has_phone: bool | None = Query(None),
    has_email: bool | None = Query(None),
    has_social: bool | None = Query(None),
    has_website: bool | None = Query(None),
    min_score: int | None = Query(None, ge=0, le=100),
    status: BusinessStatus | None = Query(None),
    sort: str = Query("discovered_at_desc"),
    db: Session = Depends(get_db),
) -> BusinessListResponse:
    base = build_filtered_leads_query(
        search=search,
        country=country,
        state=state,
        city=city,
        category=category,
        min_rating=min_rating,
        min_reviews=min_reviews,
        has_phone=has_phone,
        has_email=has_email,
        has_social=has_social,
        has_website=has_website,
        min_score=min_score,
        status=status,
    )

    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()

    stmt = (
        base.order_by(_SORT_OPTIONS.get(sort, _SORT_OPTIONS["discovered_at_desc"]))
        .offset(offset)
        .limit(limit)
        .options(
            selectinload(Business.locations),
            selectinload(Business.websites).selectinload(BusinessWebsite.analysis),
            selectinload(Business.socials),
            selectinload(Business.contacts),
            selectinload(Business.lead_score),
        )
    )
    businesses = db.execute(stmt).unique().scalars().all()
    return BusinessListResponse(count=total, results=[_to_list_item(b) for b in businesses])


@router.get("/export")
def export_leads(
    search: str | None = Query(None),
    country: str | None = Query(None),
    state: str | None = Query(None),
    city: str | None = Query(None),
    category: str | None = Query(None),
    min_rating: float | None = Query(None, ge=0, le=5),
    min_reviews: int | None = Query(None, ge=0),
    has_phone: bool | None = Query(None),
    has_email: bool | None = Query(None),
    has_social: bool | None = Query(None),
    has_website: bool | None = Query(None),
    min_score: int | None = Query(None, ge=0, le=100),
    status: BusinessStatus | None = Query(None),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    base = build_filtered_leads_query(
        search=search,
        country=country,
        state=state,
        city=city,
        category=category,
        min_rating=min_rating,
        min_reviews=min_reviews,
        has_phone=has_phone,
        has_email=has_email,
        has_social=has_social,
        has_website=has_website,
        min_score=min_score,
        status=status,
    )
    stmt = base.order_by(Business.discovered_at.desc()).options(
        selectinload(Business.locations),
        selectinload(Business.websites).selectinload(BusinessWebsite.analysis),
        selectinload(Business.socials),
        selectinload(Business.contacts),
        selectinload(Business.lead_score),
    )
    businesses = db.execute(stmt).unique().scalars().all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "Business Name",
            "Category",
            "Country",
            "City",
            "Address",
            "Phone",
            "Email",
            "Facebook",
            "Instagram",
            "Website",
            "Website Score",
            "Lead Score",
            "Status",
            "Source",
        ]
    )
    for business in businesses:
        location = business.locations[0] if business.locations else None
        website = business.websites[0] if business.websites else None
        phone = next((c.value for c in business.contacts if c.type == ContactType.PHONE), "")
        email = next((c.value for c in business.contacts if c.type == ContactType.EMAIL), "")
        facebook = next(
            (s.url for s in business.socials if s.platform == SocialPlatform.FACEBOOK), ""
        )
        instagram = next(
            (s.url for s in business.socials if s.platform == SocialPlatform.INSTAGRAM), ""
        )
        writer.writerow(
            [
                business.name,
                business.category or "",
                location.country if location else "",
                location.city if location else "",
                location.address if location else "",
                phone,
                email,
                facebook,
                instagram,
                website.url if website and website.url else "",
                website.analysis.quality_score if website and website.analysis else "",
                business.lead_score.score if business.lead_score else "",
                business.status.value,
                business.source or "",
            ]
        )

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads_export.csv"},
    )


@router.get("/{business_id}", response_model=BusinessDetail)
def get_lead(business_id: uuid.UUID, db: Session = Depends(get_db)) -> BusinessDetail:
    business = (
        db.execute(
            select(Business)
            .where(Business.id == business_id)
            .options(
                selectinload(Business.locations),
                selectinload(Business.websites).selectinload(BusinessWebsite.analysis),
                selectinload(Business.socials),
                selectinload(Business.contacts),
                selectinload(Business.lead_score),
            )
        )
        .scalars()
        .first()
    )
    if business is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return _to_detail(business)


@router.patch("/{business_id}/status", response_model=BusinessDetail)
def update_lead_status(
    business_id: uuid.UUID,
    payload: BusinessStatusUpdate,
    db: Session = Depends(get_db),
) -> BusinessDetail:
    business = db.get(
        Business, business_id, options=[selectinload(Business.contacts)]
    )
    if business is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    business.status = payload.status

    if payload.status == BusinessStatus.DO_NOT_CONTACT:
        for contact in business.contacts:
            if contact.type == ContactType.EMAIL:
                exists = db.execute(
                    select(UnsubscribedEmail).where(UnsubscribedEmail.email == contact.value)
                ).scalars().first()
                if exists is None:
                    db.add(UnsubscribedEmail(email=contact.value))

    db.commit()
    return get_lead(business_id, db)
