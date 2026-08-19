import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    BusinessStatus,
    CampaignLeadStatus,
    CampaignStatus,
    MessageChannel,
    MessageStatus,
)


class MessageTemplateCreate(BaseModel):
    name: str
    subject: str
    body: str


class MessageTemplateUpdate(BaseModel):
    name: str | None = None
    subject: str | None = None
    body: str | None = None


class MessageTemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    subject: str
    body: str
    created_at: datetime


LEAD_FILTER_FIELDS = (
    "search",
    "country",
    "state",
    "city",
    "category",
    "min_rating",
    "min_reviews",
    "has_phone",
    "has_email",
    "has_social",
    "has_website",
    "min_score",
    "status",
)


class CampaignCreate(BaseModel):
    name: str
    template_id: uuid.UUID
    daily_send_limit: int = Field(default=20, ge=1, le=500)
    follow_up_days: int | None = Field(default=None, ge=1, le=60)

    search: str | None = None
    country: str | None = None
    state: str | None = None
    city: str | None = None
    category: str | None = None
    min_rating: float | None = Field(default=None, ge=0, le=5)
    min_reviews: int | None = Field(default=None, ge=0)
    has_phone: bool | None = None
    has_email: bool | None = None
    has_social: bool | None = None
    has_website: bool | None = None
    min_score: int | None = Field(default=None, ge=0, le=100)
    status: BusinessStatus | None = None

    def filter_kwargs(self) -> dict:
        return self.model_dump(include=set(LEAD_FILTER_FIELDS))


class CampaignUpdate(BaseModel):
    status: CampaignStatus | None = None
    daily_send_limit: int | None = Field(default=None, ge=1, le=500)


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    business_id: uuid.UUID
    channel: MessageChannel
    subject: str
    body: str
    status: MessageStatus
    sent_at: datetime | None


class MessageUpdate(BaseModel):
    subject: str | None = None
    body: str | None = None


class CampaignLeadRead(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    business_name: str
    profile_url: str | None
    status: CampaignLeadStatus
    message: MessageRead | None


class CampaignRead(BaseModel):
    id: uuid.UUID
    name: str
    template_id: uuid.UUID
    filter_params: dict
    daily_send_limit: int
    follow_up_days: int | None
    status: CampaignStatus
    created_at: datetime
    lead_count: int
    pending_approval_count: int
    approved_count: int
    sent_count: int
    failed_count: int


class CampaignDetail(CampaignRead):
    leads: list[CampaignLeadRead]


class CampaignProcessResult(BaseModel):
    sent: int
    failed: int
    skipped: int
