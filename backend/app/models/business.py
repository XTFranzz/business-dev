import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import (
    BusinessStatus,
    ContactType,
    SocialPlatform,
    WebsiteStatus,
)
from app.models.mixins import TimestampMixin, UUIDPkMixin


def _enum(py_enum):
    return Enum(
        py_enum,
        native_enum=False,
        create_constraint=False,
        validate_strings=True,
        values_callable=lambda e: [member.value for member in e],
    )


class Business(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "businesses"

    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[BusinessStatus] = mapped_column(
        _enum(BusinessStatus), default=BusinessStatus.NEW, nullable=False
    )
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    rating: Mapped[float | None] = mapped_column(Numeric(2, 1), nullable=True)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    locations: Mapped[list["BusinessLocation"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    contacts: Mapped[list["BusinessContact"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    socials: Mapped[list["BusinessSocial"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    websites: Mapped[list["BusinessWebsite"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    lead_score: Mapped["LeadScore | None"] = relationship(
        back_populates="business", cascade="all, delete-orphan", uselist=False
    )


class BusinessLocation(Base, UUIDPkMixin):
    __tablename__ = "business_locations"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE")
    )
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)

    business: Mapped["Business"] = relationship(back_populates="locations")


class BusinessContact(Base, UUIDPkMixin):
    __tablename__ = "business_contacts"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE")
    )
    type: Mapped[ContactType] = mapped_column(_enum(ContactType))
    value: Mapped[str] = mapped_column(String(255))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    business: Mapped["Business"] = relationship(back_populates="contacts")


class BusinessSocial(Base, UUIDPkMixin):
    __tablename__ = "business_socials"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE")
    )
    platform: Mapped[SocialPlatform] = mapped_column(_enum(SocialPlatform))
    url: Mapped[str] = mapped_column(Text)

    business: Mapped["Business"] = relationship(back_populates="socials")


class BusinessWebsite(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "business_websites"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE")
    )
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[WebsiteStatus] = mapped_column(
        _enum(WebsiteStatus), default=WebsiteStatus.NEEDS_REVIEW, nullable=False
    )

    business: Mapped["Business"] = relationship(back_populates="websites")
    analysis: Mapped["WebsiteAnalysis | None"] = relationship(
        back_populates="website", cascade="all, delete-orphan", uselist=False
    )


class WebsiteAnalysis(Base, UUIDPkMixin):
    __tablename__ = "website_analysis"

    website_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("business_websites.id", ondelete="CASCADE"),
        unique=True,
    )
    http_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    https: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    ssl_valid: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    final_redirect_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    mobile_viewport_present: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    load_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pages_crawled: Mapped[int | None] = mapped_column(Integer, nullable=True)
    has_contact_form: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_booking_form: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    broken_links_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seo_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quality_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    website: Mapped["BusinessWebsite"] = relationship(back_populates="analysis")


class LeadScore(Base, UUIDPkMixin):
    __tablename__ = "lead_scores"
    __table_args__ = (UniqueConstraint("business_id"),)

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE")
    )
    score: Mapped[int] = mapped_column(Integer)
    reasons: Mapped[list[str]] = mapped_column(JSONB, default=list)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    business: Mapped["Business"] = relationship(back_populates="lead_score")
