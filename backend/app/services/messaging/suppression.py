from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Business, UnsubscribedEmail
from app.models.enums import BusinessStatus


def is_suppressed(db: Session, business: Business, email: str | None) -> str | None:
    """Returns a reason string if this business/email should not be contacted, else None."""
    if business.status == BusinessStatus.DO_NOT_CONTACT:
        return "business is marked Do Not Contact"

    if email:
        unsub = db.execute(
            select(UnsubscribedEmail).where(UnsubscribedEmail.email == email)
        ).scalars().first()
        if unsub is not None:
            return "email address unsubscribed"

    return None
