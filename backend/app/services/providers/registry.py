from app.core.config import get_settings
from app.services.providers.base import BusinessProvider
from app.services.providers.google_places import GooglePlacesProvider


class ProviderNotConfiguredError(RuntimeError):
    pass


def get_discovery_provider(name: str = "google_places") -> BusinessProvider:
    settings = get_settings()
    if name == "google_places":
        if not settings.google_places_api_key:
            raise ProviderNotConfiguredError("GOOGLE_PLACES_API_KEY is not set in backend/.env")
        return GooglePlacesProvider(api_key=settings.google_places_api_key)
    raise ValueError(f"Unknown discovery provider: {name}")
