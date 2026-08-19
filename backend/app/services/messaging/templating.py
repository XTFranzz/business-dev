import re

from app.models import Business

_PLACEHOLDER_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def _template_vars(business: Business) -> dict[str, str]:
    location = business.locations[0] if business.locations else None
    website = business.websites[0] if business.websites else None
    social_platforms = ", ".join(s.platform.value.title() for s in business.socials)

    if not website or not website.url:
        website_status = "no website"
    else:
        website_status = website.status.value.replace("_", " ")

    return {
        "business_name": business.name,
        "city": (location.city if location and location.city else "your area"),
        "category": business.category or "business",
        "website_status": website_status,
        "social_platform": social_platforms or "social media",
        "lead_score": str(business.lead_score.score) if business.lead_score else "",
    }


def render_template(text: str, business: Business) -> str:
    variables = _template_vars(business)

    def _replace(match: re.Match) -> str:
        key = match.group(1)
        return variables.get(key, match.group(0))

    return _PLACEHOLDER_RE.sub(_replace, text)
