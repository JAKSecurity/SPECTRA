import hashlib
import re
from datetime import datetime, timezone
from html import unescape

import feedparser as _feedparser

from .base import BaseFetcher, FetchedItem, FetchResult


def _strip_html(text: str) -> str:
    """Remove HTML tags and decode entities from RSS summary text."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


class _FeedparserProxy:
    """Thin proxy around feedparser so tests can patch rss.feedparser.parse
    independently of the global feedparser module."""

    def parse(self, url_or_string: str):
        return _feedparser.parse(url_or_string)


feedparser = _FeedparserProxy()


class RSSFetcher(BaseFetcher):
    def fetch(self) -> FetchResult:
        url = self.config["url"]
        category_hint = self.config.get("category_hint", "news")

        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries:
            link = entry.get("link", entry.get("id", ""))
            item_id = hashlib.sha256(link.encode()).hexdigest()[:16]

            published = ""
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")

            items.append(
                FetchedItem(
                    id=item_id,
                    title=_strip_html(entry.get("title", "")),
                    url=link,
                    published=published,
                    summary=_strip_html(entry.get("summary", "")),
                    category_hint=category_hint,
                )
            )

        return FetchResult(
            source=self.name,
            fetched_at=datetime.now(timezone.utc).isoformat(),
            items=items,
        )
