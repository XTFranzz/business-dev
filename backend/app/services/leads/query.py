from sqlalchemy import Select, select

from app.models import Business, BusinessContact, BusinessLocation, BusinessWebsite, LeadScore
from app.models.enums import BusinessStatus, ContactType, WebsiteStatus


def build_filtered_leads_query(
    *,
    search: str | None = None,
    country: str | None = None,
    state: str | None = None,
    city: str | None = None,
    category: str | None = None,
    min_rating: float | None = None,
    min_reviews: int | None = None,
    has_phone: bool | None = None,
    has_email: bool | None = None,
    has_social: bool | None = None,
    has_website: bool | None = None,
    min_score: int | None = None,
    status: BusinessStatus | None = None,
) -> Select:
    stmt = (
        select(Business)
        .outerjoin(BusinessLocation, BusinessLocation.business_id == Business.id)
        .outerjoin(BusinessWebsite, BusinessWebsite.business_id == Business.id)
        .outerjoin(LeadScore, LeadScore.business_id == Business.id)
    )

    if search:
        stmt = stmt.where(Business.name.ilike(f"%{search}%"))
    if category:
        stmt = stmt.where(Business.category.ilike(f"%{category}%"))
    if status:
        stmt = stmt.where(Business.status == status)
    if country:
        stmt = stmt.where(BusinessLocation.country.ilike(f"%{country}%"))
    if state:
        stmt = stmt.where(BusinessLocation.state.ilike(f"%{state}%"))
    if city:
        stmt = stmt.where(BusinessLocation.city.ilike(f"%{city}%"))
    if min_rating is not None:
        stmt = stmt.where(Business.rating >= min_rating)
    if min_reviews is not None:
        stmt = stmt.where(Business.review_count >= min_reviews)
    if has_website is True:
        stmt = stmt.where(BusinessWebsite.status != WebsiteStatus.NONE)
    elif has_website is False:
        stmt = stmt.where(
            (BusinessWebsite.status == WebsiteStatus.NONE) | (BusinessWebsite.url.is_(None))
        )
    if min_score is not None:
        stmt = stmt.where(LeadScore.score >= min_score)
    if has_phone is True:
        stmt = stmt.where(Business.contacts.any(BusinessContact.type == ContactType.PHONE))
    elif has_phone is False:
        stmt = stmt.where(~Business.contacts.any(BusinessContact.type == ContactType.PHONE))
    if has_email is True:
        stmt = stmt.where(Business.contacts.any(BusinessContact.type == ContactType.EMAIL))
    elif has_email is False:
        stmt = stmt.where(~Business.contacts.any(BusinessContact.type == ContactType.EMAIL))
    if has_social is True:
        stmt = stmt.where(Business.socials.any())
    elif has_social is False:
        stmt = stmt.where(~Business.socials.any())

    return stmt.distinct()
