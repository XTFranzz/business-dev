import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import BusinessStatus, ContactType, SocialPlatform, WebsiteStatus


class SocialRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    platform: SocialPlatform
    url: str


class ContactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    type: ContactType
    value: str
    is_primary: bool


class LocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    country: str | None
    state: str | None
    city: str | None
    postal_code: str | None
    address: str | None
    latitude: float | None
    longitude: float | None


class WebsiteAnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    http_status: int | None
    https: bool | None
    ssl_valid: bool | None
    final_redirect_url: str | None
    page_title: str | None
    meta_description: str | None
    mobile_viewport_present: bool | None
    load_time_ms: int | None
    pages_crawled: int | None
    has_contact_form: bool | None
    has_booking_form: bool | None
    broken_links_count: int | None
    seo_score: int | None
    quality_score: int | None
    analyzed_at: datetime


class WebsiteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    url: str | None
    status: WebsiteStatus
    analysis: WebsiteAnalysisRead | None = None


class LeadScoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    score: int
    reasons: list[str]
    computed_at: datetime


class BusinessListItem(BaseModel):
    id: uuid.UUID
    name: str
    category: str | None
    status: BusinessStatus
    rating: float | None
    review_count: int | None
    discovered_at: datetime
    location: LocationRead | None
    website: WebsiteRead | None
    socials: list[SocialRead]
    has_phone: bool
    has_email: bool
    lead_score: int | None


class BusinessListResponse(BaseModel):
    count: int
    results: list[BusinessListItem]


class BusinessDetail(BaseModel):
    id: uuid.UUID
    name: str
    category: str | None
    description: str | None
    status: BusinessStatus
    source: str | None
    source_url: str | None
    rating: float | None
    review_count: int | None
    discovered_at: datetime
    location: LocationRead | None
    website: WebsiteRead | None
    socials: list[SocialRead]
    contacts: list[ContactRead]
    lead_score: LeadScoreRead | None


class BusinessStatusUpdate(BaseModel):
    status: BusinessStatus
