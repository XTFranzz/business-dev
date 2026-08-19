import re
import time
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import httpx
from selectolax.parser import HTMLParser

from app.models.enums import WebsiteStatus

_DIRECTORY_DOMAINS = (
    "wixsite.com",
    "weebly.com",
    "business.site",
    "godaddysites.com",
    "sites.google.com",
    "linktr.ee",
)
_SOCIAL_DOMAINS = ("facebook.com", "instagram.com", "tiktok.com", "linkedin.com")

MAX_LINKS_TO_CHECK = 3
REQUEST_TIMEOUT = 10
USER_AGENT = "Mozilla/5.0 (compatible; LeadFinderBot/1.0; +https://example.com/bot)"

_CONTACT_TEXT_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+|\+?\d[\d\s().-]{7,}\d")


@dataclass
class WebsiteAnalysisResult:
    status: WebsiteStatus
    http_status: int | None = None
    https: bool | None = None
    ssl_valid: bool | None = None
    final_redirect_url: str | None = None
    page_title: str | None = None
    meta_description: str | None = None
    mobile_viewport_present: bool | None = None
    load_time_ms: int | None = None
    pages_crawled: int | None = None
    has_contact_form: bool | None = None
    has_booking_form: bool | None = None
    broken_links_count: int | None = None
    seo_score: int | None = None
    quality_score: int | None = None


def _domain(url: str) -> str:
    netloc = (urlparse(url).netloc or "").lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


async def analyze_website(url: str) -> WebsiteAnalysisResult:
    try:
        start = time.monotonic()
        async with httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        ) as client:
            response = await client.get(url)
            load_time_ms = int((time.monotonic() - start) * 1000)
    except httpx.RequestError:
        return WebsiteAnalysisResult(status=WebsiteStatus.UNREACHABLE)

    final_url = str(response.url)
    final_domain = _domain(final_url)

    if any(social in final_domain for social in _SOCIAL_DOMAINS):
        return WebsiteAnalysisResult(
            status=WebsiteStatus.REDIRECTS_TO_SOCIAL,
            http_status=response.status_code,
            final_redirect_url=final_url,
        )

    if response.status_code >= 400:
        return WebsiteAnalysisResult(
            status=WebsiteStatus.UNREACHABLE,
            http_status=response.status_code,
            final_redirect_url=final_url if final_url != url else None,
        )

    tree = HTMLParser(response.text)
    title_node = tree.css_first("title")
    page_title = title_node.text(strip=True) if title_node else None

    meta_desc_node = tree.css_first('meta[name="description"]')
    meta_description = meta_desc_node.attributes.get("content") if meta_desc_node else None

    mobile_viewport_present = tree.css_first('meta[name="viewport"]') is not None

    body_text = tree.body.text(separator=" ", strip=True) if tree.body else ""
    has_contact_form = _has_form_matching(tree, ("contact", "email", "message"))
    has_booking_form = _has_form_matching(tree, ("book", "reservation", "appointment", "schedule"))
    has_contact_info = has_contact_form or bool(_CONTACT_TEXT_RE.search(body_text))

    internal_links = _internal_links(tree, final_url, final_domain)
    sampled_links = internal_links[:MAX_LINKS_TO_CHECK]
    broken_links_count = await _count_broken_links(sampled_links)
    pages_crawled = 1 + len(sampled_links)

    https = final_url.startswith("https")
    seo_score = _seo_score(page_title, meta_description, tree)
    quality_score = _quality_score(
        https=https,
        has_title=bool(page_title and len(page_title) > 10),
        has_meta=bool(meta_description),
        mobile_viewport=mobile_viewport_present,
        has_contact=has_contact_info,
        load_time_ms=load_time_ms,
        broken_links_count=broken_links_count,
        pages_crawled=pages_crawled,
    )
    status = _classify_status(final_domain, quality_score, page_title, meta_description)

    return WebsiteAnalysisResult(
        status=status,
        http_status=response.status_code,
        https=https,
        ssl_valid=https,
        final_redirect_url=final_url if final_url != url else None,
        page_title=page_title,
        meta_description=meta_description,
        mobile_viewport_present=mobile_viewport_present,
        load_time_ms=load_time_ms,
        pages_crawled=pages_crawled,
        has_contact_form=has_contact_form,
        has_booking_form=has_booking_form,
        broken_links_count=broken_links_count,
        seo_score=seo_score,
        quality_score=quality_score,
    )


def _has_form_matching(tree: HTMLParser, keywords: tuple[str, ...]) -> bool:
    for form in tree.css("form"):
        blob = (form.html or "").lower()
        if any(keyword in blob for keyword in keywords):
            return True
    return False


def _internal_links(tree: HTMLParser, base_url: str, domain: str) -> list[str]:
    links: list[str] = []
    seen: set[str] = {base_url}
    for anchor in tree.css("a[href]"):
        href = anchor.attributes.get("href")
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        absolute = urljoin(base_url, href)
        if _domain(absolute) != domain or absolute in seen:
            continue
        seen.add(absolute)
        links.append(absolute)
    return links


async def _count_broken_links(links: list[str]) -> int:
    if not links:
        return 0
    broken = 0
    async with httpx.AsyncClient(
        timeout=8, follow_redirects=True, headers={"User-Agent": USER_AGENT}
    ) as client:
        for link in links:
            try:
                resp = await client.head(link)
                if resp.status_code >= 400:
                    resp = await client.get(link)
                if resp.status_code >= 400:
                    broken += 1
            except httpx.RequestError:
                broken += 1
    return broken


def _seo_score(title: str | None, meta_description: str | None, tree: HTMLParser) -> int:
    score = 0
    if title and 10 <= len(title) <= 70:
        score += 40
    elif title:
        score += 20
    if meta_description and 50 <= len(meta_description) <= 160:
        score += 40
    elif meta_description:
        score += 20
    if tree.css_first("h1"):
        score += 20
    return min(score, 100)


def _quality_score(
    *,
    https: bool,
    has_title: bool,
    has_meta: bool,
    mobile_viewport: bool,
    has_contact: bool,
    load_time_ms: int,
    broken_links_count: int,
    pages_crawled: int,
) -> int:
    score = 0
    score += 15 if https else 0
    score += 10 if has_title else 0
    score += 10 if has_meta else 0
    score += 15 if mobile_viewport else 0
    score += 15 if has_contact else 0
    score += 10 if load_time_ms < 3000 else (5 if load_time_ms < 6000 else 0)
    score += 10 if broken_links_count == 0 else 0
    score += 15 if pages_crawled > 1 else 0
    return min(score, 100)


def _classify_status(
    domain: str, quality_score: int, title: str | None, meta_description: str | None
) -> WebsiteStatus:
    if any(directory_domain in domain for directory_domain in _DIRECTORY_DOMAINS):
        return WebsiteStatus.DIRECTORY
    if quality_score < 35:
        return WebsiteStatus.OUTDATED
    if quality_score < 55 or not title or not meta_description:
        return WebsiteStatus.INCOMPLETE
    return WebsiteStatus.FOUND
