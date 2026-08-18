import asyncio

import httpx

from app.services.providers.base import BusinessProvider, DiscoveredBusiness, DiscoveryParams

SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

FIELD_MASK = ",".join(
    [
        "places.id",
        "places.displayName",
        "places.formattedAddress",
        "places.addressComponents",
        "places.location",
        "places.rating",
        "places.userRatingCount",
        "places.websiteUri",
        "places.nationalPhoneNumber",
        "places.internationalPhoneNumber",
        "places.primaryType",
        "places.primaryTypeDisplayName",
        "places.businessStatus",
        "places.googleMapsUri",
        "places.editorialSummary",
        "nextPageToken",
    ]
)

# A Places "website" that's actually a social profile isn't a real website.
_SOCIAL_DOMAINS = {
    "facebook.com": "facebook",
    "instagram.com": "instagram",
    "tiktok.com": "tiktok",
    "linkedin.com": "linkedin",
}

PAGE_SIZE = 20
MAX_PAGES = 5


def _classify_website(url: str | None) -> tuple[str | None, dict[str, str]]:
    if not url:
        return None, {}
    lowered = url.lower()
    for domain, platform in _SOCIAL_DOMAINS.items():
        if domain in lowered:
            return None, {platform: url}
    return url, {}


def _address_component(components: list[dict], type_: str) -> str | None:
    for component in components or []:
        if type_ in component.get("types", []):
            return component.get("longText")
    return None


class GooglePlacesProvider(BusinessProvider):
    name = "google_places"

    def __init__(self, api_key: str):
        self._api_key = api_key

    async def search(self, params: DiscoveryParams) -> list[DiscoveredBusiness]:
        text_query = self._build_query(params)
        results: list[DiscoveredBusiness] = []
        page_token: str | None = None

        async with httpx.AsyncClient(timeout=15) as client:
            for page in range(MAX_PAGES):
                if len(results) >= params.max_results:
                    break
                if page > 0:
                    # Places API (New) needs a short delay before a pageToken is valid.
                    await asyncio.sleep(2)

                body = {"textQuery": text_query, "pageSize": PAGE_SIZE}
                if page_token:
                    body["pageToken"] = page_token

                response = await client.post(
                    SEARCH_URL,
                    headers={
                        "Content-Type": "application/json",
                        "X-Goog-Api-Key": self._api_key,
                        "X-Goog-FieldMask": FIELD_MASK,
                    },
                    json=body,
                )
                response.raise_for_status()
                data = response.json()

                results.extend(self._to_business(place) for place in data.get("places", []))

                page_token = data.get("nextPageToken")
                if not page_token:
                    break

        return results[: params.max_results]

    @staticmethod
    def _build_query(params: DiscoveryParams) -> str:
        location_parts = [p for p in [params.city, params.state, params.country] if p]
        if location_parts:
            return f"{params.category} in {', '.join(location_parts)}"
        return params.category

    @staticmethod
    def _to_business(place: dict) -> DiscoveredBusiness:
        website_url, social_urls = _classify_website(place.get("websiteUri"))
        components = place.get("addressComponents", [])
        location = place.get("location", {})

        return DiscoveredBusiness(
            name=place.get("displayName", {}).get("text", "Unknown"),
            source="google_places",
            source_id=place.get("id"),
            source_url=place.get("googleMapsUri"),
            category=(place.get("primaryTypeDisplayName") or {}).get("text")
            or place.get("primaryType"),
            description=(place.get("editorialSummary") or {}).get("text"),
            rating=place.get("rating"),
            review_count=place.get("userRatingCount"),
            business_status=place.get("businessStatus"),
            country=_address_component(components, "country"),
            state=_address_component(components, "administrative_area_level_1"),
            city=(
                _address_component(components, "locality")
                or _address_component(components, "administrative_area_level_2")
            ),
            postal_code=_address_component(components, "postal_code"),
            address=place.get("formattedAddress"),
            latitude=location.get("latitude"),
            longitude=location.get("longitude"),
            phone=place.get("nationalPhoneNumber") or place.get("internationalPhoneNumber"),
            email=None,
            website_url=website_url,
            social_urls=social_urls,
            raw_payload=place,
        )
