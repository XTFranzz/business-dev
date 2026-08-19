from dataclasses import dataclass

from app.models.enums import WebsiteStatus

QUALIFY_THRESHOLD = 60


@dataclass
class ScoringInput:
    has_website: bool
    website_status: WebsiteStatus | None
    website_quality_score: int | None
    rating: float | None
    review_count: int | None
    has_phone: bool
    has_email: bool
    social_platform_count: int


def compute_lead_score(data: ScoringInput) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []

    if data.social_platform_count > 0:
        score += 10
        reasons.append("Active social media presence")

    if data.review_count and data.review_count >= 20:
        score += 10
        reasons.append(f"{data.review_count}+ reviews")
    if data.review_count and data.review_count >= 100:
        score += 10
        reasons.append("100+ reviews — high customer activity")

    if not data.has_website:
        score += 30
        reasons.append("No website")
    elif data.website_status == WebsiteStatus.OUTDATED:
        score += 20
        reasons.append("Website appears outdated")
    elif data.website_status == WebsiteStatus.UNREACHABLE:
        score += 10
        reasons.append("Website is unreachable")
    elif data.website_status == WebsiteStatus.INCOMPLETE:
        score += 10
        reasons.append("Website appears incomplete")
    elif data.website_quality_score is not None and data.website_quality_score < 50:
        score += 10
        reasons.append("Website has a poor visitor experience")

    if data.has_email:
        score += 10
        reasons.append("Public business email")
    if data.has_phone:
        score += 5
        reasons.append("Public phone number")

    if data.rating and data.rating >= 4.5 and data.review_count and data.review_count >= 50:
        score += 10
        reasons.append("Strong customer reviews")

    return min(score, 100), reasons
