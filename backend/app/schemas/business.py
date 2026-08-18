import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import BusinessStatus, SocialPlatform, WebsiteStatus


class SocialRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    platform: SocialPlatform
    url: str


class LocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    country: str | None
    state: str | None
    city: str | None
    address: str | None


class WebsiteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    url: str | None
    status: WebsiteStatus


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


class BusinessListResponse(BaseModel):
    count: int
    results: list[BusinessListItem]
