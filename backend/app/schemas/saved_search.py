import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SavedSearchCreate(BaseModel):
    name: str
    country: str
    category: str
    state: str | None = None
    city: str | None = None
    max_results: int = 20


class SavedSearchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    params: dict
    created_at: datetime
