import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import SearchJobStatus


class DiscoverJobCreate(BaseModel):
    country: str
    category: str
    state: str | None = None
    city: str | None = None
    max_results: int = Field(default=20, ge=1, le=60)
    provider: str = "google_places"


class DiscoverJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: SearchJobStatus
    found_count: int
    processed_count: int
    checked_count: int
    qualified_count: int
    error: str | None
    started_at: datetime | None
    completed_at: datetime | None
