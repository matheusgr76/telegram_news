"""
news_fetcher.py
Fetches top headlines from NewsAPI.org and The News API,
normalises them into a shared schema, and groups by section.
"""
import logging
from typing import TypedDict

import httpx

import config

logger = logging.getLogger(__name__)

NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"
THENEWSAPI_URL = "https://api.thenewsapi.com/v1/news/top"

# Section → (newsapi_category, thenewsapi_categories)
SECTION_MAP = {
    "biggest_story": ("general", "general"),
    "markets":       ("business", "business"),
    "us_domestic":   ("general", "politics"),
    "tech_business": ("technology", "tech"),
}


class Article(TypedDict):
    title: str
    description: str
    source: str
    url: str
    section: str


# ── Normalisers ──────────────────────────────────────────────────────────────

def _from_newsapi(item: dict, section: str) -> Article:
    return Article(
        title=item.get("title") or "",
        description=item.get("description") or "",
        source=item.get("source", {}).get("name") or "NewsAPI",
        url=item.get("url") or "",
        section=section,
    )


def _from_thenewsapi(item: dict, section: str) -> Article:
    return Article(
        title=item.get("title") or "",
        description=item.get("description") or "",
        source=item.get("source") or "TheNewsAPI",
        url=item.get("url") or "",
        section=section,
    )


# ── Fetchers ─────────────────────────────────────────────────────────────────

async def _fetch_newsapi(client: httpx.AsyncClient, category: str, section: str) -> list[Article]:
    try:
        resp = await client.get(
            NEWSAPI_URL,
            params={"apiKey": config.NEWSAPI_KEY, "country": "us",
                    "category": category, "pageSize": 5},
        )
        resp.raise_for_status()
        items = resp.json().get("articles", [])
        return [_from_newsapi(a, section) for a in items if a.get("title")]
    except Exception as exc:
        logger.warning("NewsAPI fetch failed for %s: %s", category, exc)
        return []


async def _fetch_thenewsapi(client: httpx.AsyncClient, categories: str, section: str) -> list[Article]:
    try:
        resp = await client.get(
            THENEWSAPI_URL,
            params={"api_token": config.THENEWSAPI_KEY, "locale": "us",
                    "categories": categories, "limit": 5},
        )
        resp.raise_for_status()
        items = resp.json().get("data", [])
        return [_from_thenewsapi(a, section) for a in items if a.get("title")]
    except Exception as exc:
        logger.warning("TheNewsAPI fetch failed for %s: %s", categories, exc)
        return []


# ── Public API ────────────────────────────────────────────────────────────────

async def fetch_all_news() -> dict[str, list[Article]]:
    """
    Returns articles grouped by section key.
    Each section has up to 10 articles (5 from each API).
    """
    results: dict[str, list[Article]] = {k: [] for k in SECTION_MAP}

    async with httpx.AsyncClient(timeout=config.HTTP_TIMEOUT_SECONDS) as client:
        for section, (newsapi_cat, thenews_cat) in SECTION_MAP.items():
            newsapi_articles = await _fetch_newsapi(client, newsapi_cat, section)
            thenews_articles = await _fetch_thenewsapi(client, thenews_cat, section)
            results[section] = newsapi_articles + thenews_articles
            logger.info("Section '%s': %d articles fetched", section, len(results[section]))

    return results
