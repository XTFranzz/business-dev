import re
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Business, BusinessContact, BusinessLocation, BusinessWebsite
from app.models.enums import ContactType
from app.services.providers.base import DiscoveredBusiness


def _normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _domain(url: str | None) -> str | None:
    if not url:
        return None
    netloc = urlparse(url).netloc or urlparse(url).path
    netloc = netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def find_existing_business(db: Session, discovered: DiscoveredBusiness) -> Business | None:
    domain = _domain(discovered.website_url)
    if domain:
        website = (
            db.execute(select(BusinessWebsite).where(BusinessWebsite.url.ilike(f"%{domain}%")))
            .scalars()
            .first()
        )
        if website:
            return website.business

    if discovered.phone:
        contact = (
            db.execute(
                select(BusinessContact).where(
                    BusinessContact.type == ContactType.PHONE,
                    BusinessContact.value == discovered.phone,
                )
            )
            .scalars()
            .first()
        )
        if contact:
            return contact.business

    if discovered.city:
        target_name = _normalize_name(discovered.name)
        candidates = (
            db.execute(
                select(Business)
                .join(BusinessLocation)
                .where(BusinessLocation.city == discovered.city)
            )
            .scalars()
            .all()
        )
        for candidate in candidates:
            if _normalize_name(candidate.name) == target_name:
                return candidate

    return None
