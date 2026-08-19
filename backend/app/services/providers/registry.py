from app.core.config import get_settings
from app.services.providers.base import BusinessProvider
from app.services.providers.google_places import GooglePlacesProvider
from app.services.providers.overpass import OverpassProvider

DISCOVERY_PROVIDERS = ("google_places", "overpass")


class ProviderNotConfiguredError(RuntimeError):
    pass


def get_discovery_provider(name: str = "google_places") -> BusinessProvider:
    settings = get_settings()
    if name == "google_places":
        if not settings.google_places_api_key:
            raise ProviderNotConfiguredError("GOOGLE_PLACES_API_KEY is not set in backend/.env")
        return GooglePlacesProvider(api_key=settings.google_places_api_key)
    if name == "overpass":
        return OverpassProvider()
    raise ValueError(f"Unknown discovery provider: {name}")
