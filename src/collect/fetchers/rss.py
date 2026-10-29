import hashlib
import logging
import re
from datetime import datetime, timezone
from html import unescape
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests
import feedparser as _feedparser

from .base import BaseFetcher, FetchedItem, FetchResult

USER_AGENT = "SPECTRA-monthly-report/1.0 (+https://github.com/JAKSecurity/SPECTRA)"
logger = logging.getLogger(__name__)


def _page_url(url: str, page: int) -> str:
    parts = urlsplit(url)
    query = [(key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True)
             if key != "paged"]
    query.append(("paged", str(page)))
    return urlunsplit(parts._replace(query=urlencode(query)))


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
        # requests follows redirects and bounds network waits; parse the response body.
        response = requests.get(url_or_string, headers={"User-Agent": USER_AGENT}, timeout=30)
        response.raise_for_status()
        return _feedparser.parse(response.content)


feedparser = _FeedparserProxy()


class RSSFetcher(BaseFetcher):
    def fetch(self) -> FetchResult:
        url = self.config["url"]
        category_hint = self.config.get("category_hint", "news")

        paged = self.config.get("paged", False)
        max_pages = max(1, min(10, int(self.config.get("max_pages", 1)))) if paged else 1
        start_date = self.config.get("start_date")
        end_date = self.config.get("end_date")
        items = []
        seen = set()
        for page in range(1, max_pages + 1):
            try:
                feed = feedparser.parse(url if page == 1 else _page_url(url, page))
            except requests.HTTPError as exc:
                if paged and page > 1 and exc.response is not None and exc.response.status_code == 404:
                    break
                raise
            if not feed.entries:
                break
            dates = []
            for entry in feed.entries:
                published = ""
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")
                dates.append(published)
                if start_date and (not published or published < start_date):
                    continue
                if end_date and (not published or published >= end_date):
                    continue
                item = self._item(entry, published, category_hint)
                if paged and item.id in seen:
                    continue
                seen.add(item.id)
                items.append(item)
            # WHY: undated entries cannot prove that a whole page predates the window.
            if start_date and all(date and date < start_date for date in dates):
                break
            if paged and page == max_pages:
                logger.warning("Feed %s reached page cap (%d); coverage may be incomplete",
                               self.name, max_pages)

        return FetchResult(
            source=self.name,
            fetched_at=datetime.now(timezone.utc).isoformat(),
            items=items,
        )

    @staticmethod
    def _item(entry, published: str, category_hint: str) -> FetchedItem:
        link = entry.get("link", "")
        # WHY: landing pages can host distinct entries; feed IDs are not reader URLs.
        identity = (entry.get("id") or "").strip() or (entry.get("guid") or "").strip() or link
        item_id = hashlib.sha256(identity.encode()).hexdigest()[:16]

        return FetchedItem(
            id=item_id,
            title=_strip_html(entry.get("title", "")),
            url=link,
            published=published,
            summary=_strip_html(entry.get("summary", "")),
            category_hint=category_hint,
        )
