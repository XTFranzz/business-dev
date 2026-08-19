import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import (
    CampaignLeadStatus,
    CampaignStatus,
    MessageChannel,
    MessageEventType,
    MessageStatus,
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


class MessageTemplate(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "message_templates"

    name: Mapped[str] = mapped_column(String(255), unique=True)
    subject: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)


class Campaign(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "campaigns"

    name: Mapped[str] = mapped_column(String(255))
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("message_templates.id", ondelete="RESTRICT")
    )
    filter_params: Mapped[dict] = mapped_column(JSONB, default=dict)
    daily_send_limit: Mapped[int] = mapped_column(Integer, default=20)
    follow_up_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[CampaignStatus] = mapped_column(
        _enum(CampaignStatus), default=CampaignStatus.DRAFT
    )

    template: Mapped["MessageTemplate"] = relationship()
    campaign_leads: Mapped[list["CampaignLead"]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )


class CampaignLead(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "campaign_leads"
    __table_args__ = (UniqueConstraint("campaign_id", "business_id"),)

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE")
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE")
    )
    status: Mapped[CampaignLeadStatus] = mapped_column(
        _enum(CampaignLeadStatus), default=CampaignLeadStatus.PENDING
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    campaign: Mapped["Campaign"] = relationship(back_populates="campaign_leads")
    business: Mapped["Business"] = relationship()  # noqa: F821
    message: Mapped["Message | None"] = relationship(
        back_populates="campaign_lead", cascade="all, delete-orphan", uselist=False
    )


class Message(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "messages"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE")
    )
    campaign_lead_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaign_leads.id", ondelete="CASCADE"), nullable=True
    )
    channel: Mapped[MessageChannel] = mapped_column(_enum(MessageChannel))
    subject: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[MessageStatus] = mapped_column(_enum(MessageStatus), default=MessageStatus.DRAFT)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    business: Mapped["Business"] = relationship()  # noqa: F821
    campaign_lead: Mapped["CampaignLead | None"] = relationship(back_populates="message")
    events: Mapped[list["MessageEvent"]] = relationship(
        back_populates="message", cascade="all, delete-orphan"
    )


class MessageEvent(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "message_events"

    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE")
    )
    event_type: Mapped[MessageEventType] = mapped_column(_enum(MessageEventType))
    event_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    message: Mapped["Message"] = relationship(back_populates="events")


class UnsubscribedEmail(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "unsubscribed_emails"

    email: Mapped[str] = mapped_column(String(255), unique=True)
