"""
News Feed Scraper
==================
DESIGN.md §2B: Scrapes local public data / news feeds for Patna.

Supports RSS/Atom feeds via `feedparser`.
"""

from __future__ import annotations

from dataclasses import dataclass

import feedparser


# ── Default Patna-related news feeds ────────────────────
DEFAULT_FEEDS: list[str] = [
    "https://news.google.com/rss/search?q=Patna+Bihar&hl=en-IN&gl=IN&ceid=IN:en",
]

REQUEST_TIMEOUT = 15  # seconds


@dataclass
class NewsArticle:
    """A single scraped news article."""
    title: str
    summary: str
    link: str
    published: str | None = None


def fetch_rss_feed(feed_url: str, limit: int = 10) -> list[NewsArticle]:
    """
    Parse an RSS/Atom feed and return structured articles.

    Parameters
    ----------
    feed_url : str
        URL of the RSS feed.
    limit: int
        Max articles to parse

    Returns
    -------
    list[NewsArticle]
        Parsed articles from the feed.
    """
    parsed = feedparser.parse(feed_url)
    articles: list[NewsArticle] = []

    for entry in parsed.entries[:limit]:
        articles.append(
            NewsArticle(
                title=entry.get("title", ""),
                summary=entry.get("summary", entry.get("description", "")),
                link=entry.get("link", ""),
                published=entry.get("published", None),
            )
        )

    return articles


def fetch_all_feeds(
    feed_urls: list[str] | None = None,
) -> list[NewsArticle]:
    """
    Aggregate top 10 articles from all configured RSS feeds.

    Parameters
    ----------
    feed_urls : list[str] | None
        Override default feeds. If None, uses DEFAULT_FEEDS.
    """
    urls = feed_urls or DEFAULT_FEEDS
    all_articles: list[NewsArticle] = []

    for url in urls:
        try:
            all_articles.extend(fetch_rss_feed(url, limit=10))
        except Exception as e:
            print(f"[Scraper] Failed to fetch {url}: {e}")

    return all_articles
