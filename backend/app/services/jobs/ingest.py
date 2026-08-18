from sqlalchemy.orm import Session

from app.models import Business, BusinessContact, BusinessLocation, BusinessSocial, BusinessWebsite
from app.models.enums import ContactType, SocialPlatform, WebsiteStatus
from app.services.providers.base import DiscoveredBusiness


def create_business_from_discovery(db: Session, discovered: DiscoveredBusiness) -> Business:
    business = Business(
        name=discovered.name,
        category=discovered.category,
        description=discovered.description,
        source=discovered.source,
        source_url=discovered.source_url,
        rating=discovered.rating,
        review_count=discovered.review_count,
    )
    business.locations.append(
        BusinessLocation(
            country=discovered.country,
            state=discovered.state,
            city=discovered.city,
            postal_code=discovered.postal_code,
            address=discovered.address,
            latitude=discovered.latitude,
            longitude=discovered.longitude,
        )
    )
    if discovered.phone:
        business.contacts.append(
            BusinessContact(type=ContactType.PHONE, value=discovered.phone, is_primary=True)
        )
    if discovered.email:
        business.contacts.append(
            BusinessContact(type=ContactType.EMAIL, value=discovered.email, is_primary=True)
        )
    for platform, url in discovered.social_urls.items():
        business.socials.append(BusinessSocial(platform=SocialPlatform(platform), url=url))

    website_status = WebsiteStatus.FOUND if discovered.website_url else WebsiteStatus.NONE
    business.websites.append(BusinessWebsite(url=discovered.website_url, status=website_status))

    db.add(business)
    db.flush()
    return business
