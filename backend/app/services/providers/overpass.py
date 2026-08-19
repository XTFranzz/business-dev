import asyncio

import httpx

from app.services.providers.base import BusinessProvider, DiscoveredBusiness, DiscoveryParams

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
# Nominatim's usage policy asks for an honest identifying UA. Note: overpass-api.de's WAF
# rejects (406) UAs that impersonate a browser (e.g. "Mozilla/5.0 (compatible; ...)"), so this
# must stay a plain, honest bot identifier rather than a browser-spoofing string.
USER_AGENT = "LeadFinderBot/1.0"

# OpenStreetMap has no single free-text category search like Google Places - each category
# maps to a specific tag. This covers common small-business categories; anything else falls
# back to a best-effort name-text search, which may return few or no results.
_CATEGORY_TAGS: dict[str, tuple[str, str]] = {
    "restaurant": ("amenity", "restaurant"),
    "restaurants": ("amenity", "restaurant"),
    "cafe": ("amenity", "cafe"),
    "cafes": ("amenity", "cafe"),
    "coffee shop": ("amenity", "cafe"),
    "coffee shops": ("amenity", "cafe"),
    "bakery": ("shop", "bakery"),
    "bakeries": ("shop", "bakery"),
    "bar": ("amenity", "bar"),
    "bars": ("amenity", "bar"),
    "hotel": ("tourism", "hotel"),
    "hotels": ("tourism", "hotel"),
    "hairdresser": ("shop", "hairdresser"),
    "hair salon": ("shop", "hairdresser"),
    "beauty salon": ("shop", "beauty"),
    "gym": ("leisure", "fitness_centre"),
    "gyms": ("leisure", "fitness_centre"),
    "pharmacy": ("amenity", "pharmacy"),
    "pharmacies": ("amenity", "pharmacy"),
    "supermarket": ("shop", "supermarket"),
    "grocery store": ("shop", "supermarket"),
    "hardware store": ("shop", "hardware"),
    "hardware stores": ("shop", "hardware"),
    "clothing store": ("shop", "clothes"),
    "bookstore": ("shop", "books"),
    "dental clinic": ("amenity", "dentist"),
    "dental clinics": ("amenity", "dentist"),
    "dentist": ("amenity", "dentist"),
    "clinic": ("amenity", "clinic"),
    "car repair": ("shop", "car_repair"),
    "auto repair": ("shop", "car_repair"),
    "real estate agency": ("office", "estate_agent"),
}


class OverpassProvider(BusinessProvider):
    """Free OpenStreetMap-based provider - no API key or billing required."""

    name = "overpass"

    async def search(self, params: DiscoveryParams) -> list[DiscoveredBusiness]:
        bbox = await self._geocode_bbox(params)
        if bbox is None:
            return []

        tag_key, tag_value = _CATEGORY_TAGS.get(params.category.strip().lower(), (None, None))

        if tag_key:
            tag_filter = f'["{tag_key}"="{tag_value}"]'
        else:
            escaped = params.category.replace('"', "")
            tag_filter = f'["name"~"{escaped}",i]'

        south, west, north, east = bbox
        query = f"""
        [out:json][timeout:25];
        (
          nwr{tag_filter}["name"]({south},{west},{north},{east});
        );
        out center {params.max_results};
        """

        data = await self._query_overpass(query)

        return [
            self._to_business(element, params)
            for element in data.get("elements", [])[: params.max_results]
            if element.get("tags", {}).get("name")
        ]

    @staticmethod
    async def _query_overpass(query: str) -> dict:
        """The shared public overpass-api.de instance is rate-limited and known to be flaky
        (406/504/429 under load) - retry a few times before giving up."""
        last_error: Exception | None = None
        for attempt in range(3):
            if attempt > 0:
                await asyncio.sleep(3)
            try:
                async with httpx.AsyncClient(
                    timeout=30, headers={"User-Agent": USER_AGENT}
                ) as client:
                    response = await client.post(OVERPASS_URL, data={"data": query})
                    response.raise_for_status()
                    return response.json()
            except httpx.HTTPError as exc:
                last_error = exc
        raise last_error

    async def _geocode_bbox(
        self, params: DiscoveryParams
    ) -> tuple[float, float, float, float] | None:
        location_parts = [p for p in [params.city, params.state, params.country] if p]
        query = ", ".join(location_parts) if location_parts else params.country

        async with httpx.AsyncClient(timeout=15, headers={"User-Agent": USER_AGENT}) as client:
            response = await client.get(
                NOMINATIM_URL,
                params={"q": query, "format": "json", "limit": 1},
            )
            response.raise_for_status()
            results = response.json()

        if not results:
            return None
        south, north, west, east = (float(v) for v in results[0]["boundingbox"])
        return south, west, north, east

    @staticmethod
    def _to_business(element: dict, params: DiscoveryParams) -> DiscoveredBusiness:
        tags = element.get("tags", {})
        center = element.get("center", {})
        lat = element.get("lat", center.get("lat"))
        lon = element.get("lon", center.get("lon"))

        address_parts = [
            tags.get("addr:housenumber"),
            tags.get("addr:street"),
            tags.get("addr:city") or params.city,
        ]
        address = ", ".join(p for p in address_parts if p) or None

        social_urls: dict[str, str] = {}
        if tags.get("contact:facebook"):
            social_urls["facebook"] = tags["contact:facebook"]
        if tags.get("contact:instagram"):
            social_urls["instagram"] = tags["contact:instagram"]

        return DiscoveredBusiness(
            name=tags.get("name", "Unknown"),
            source="overpass",
            source_id=f"{element.get('type')}/{element.get('id')}",
            source_url=(
                f"https://www.openstreetmap.org/{element.get('type')}/{element.get('id')}"
            ),
            category=tags.get("shop") or tags.get("amenity") or tags.get("tourism"),
            description=None,
            rating=None,
            review_count=None,
            business_status="OPERATIONAL",
            country=params.country,
            state=params.state,
            city=tags.get("addr:city") or params.city,
            postal_code=tags.get("addr:postcode"),
            address=address,
            latitude=lat,
            longitude=lon,
            phone=tags.get("contact:phone") or tags.get("phone"),
            email=tags.get("contact:email") or tags.get("email"),
            website_url=tags.get("contact:website") or tags.get("website"),
            social_urls=social_urls,
            raw_payload=element,
        )
