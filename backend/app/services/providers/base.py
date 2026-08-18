from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class DiscoveryParams:
    country: str
    category: str
    state: str | None = None
    city: str | None = None
    max_results: int = 20


@dataclass
class DiscoveredBusiness:
    name: str
    source: str
    source_id: str | None = None
    source_url: str | None = None
    category: str | None = None
    description: str | None = None
    rating: float | None = None
    review_count: int | None = None
    business_status: str | None = None
    country: str | None = None
    state: str | None = None
    city: str | None = None
    postal_code: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    phone: str | None = None
    email: str | None = None
    website_url: str | None = None
    social_urls: dict[str, str] = field(default_factory=dict)
    raw_payload: dict = field(default_factory=dict)


class BusinessProvider(ABC):
    name: str

    @abstractmethod
    async def search(self, params: DiscoveryParams) -> list[DiscoveredBusiness]:
        """Return normalized businesses matching the given discovery params."""
