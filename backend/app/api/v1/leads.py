from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models import Business
from app.models.enums import ContactType
from app.schemas.business import (
    BusinessListItem,
    BusinessListResponse,
    LocationRead,
    SocialRead,
    WebsiteRead,
)

router = APIRouter(prefix="/leads", tags=["leads"])


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
    )


@router.get("", response_model=BusinessListResponse)
def list_leads(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> BusinessListResponse:
    stmt = (
        select(Business)
        .options(
            selectinload(Business.locations),
            selectinload(Business.websites),
            selectinload(Business.socials),
            selectinload(Business.contacts),
        )
        .order_by(Business.discovered_at.desc())
        .offset(offset)
        .limit(limit)
    )
    businesses = db.execute(stmt).scalars().all()
    total = db.execute(select(func.count()).select_from(Business)).scalar_one()
    return BusinessListResponse(count=total, results=[_to_list_item(b) for b in businesses])
