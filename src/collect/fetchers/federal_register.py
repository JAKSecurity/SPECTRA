import hashlib
from datetime import datetime, timezone, timedelta

import requests

from .base import BaseFetcher, FetchedItem, FetchResult
from .rss import _strip_html


class FederalRegisterFetcher(BaseFetcher):
    def fetch(self) -> FetchResult:
        search_term = self.config.get("search_term", "cybersecurity")
        days_back = self.config.get("days_back", 30)
        category_hint = self.config.get("category_hint", "policy")

        since = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%d")

        resp = requests.get(
            "https://www.federalregister.gov/api/v1/documents.json",
            params={
                "conditions[term]": search_term,
                "conditions[publication_date][gte]": since,
                "per_page": 50,
                "order": "newest",
                "fields[]": ["title", "abstract", "html_url", "publication_date", "document_number", "type"],
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        items = []
        for doc in data.get("results", []):
            doc_id = hashlib.sha256(
                doc.get("document_number", doc.get("html_url", "")).encode()
            ).hexdigest()[:16]
            abstract = _strip_html(doc.get("abstract", "") or "")
            items.append(
                FetchedItem(
                    id=doc_id,
                    title=_strip_html(doc.get("title", "")),
                    url=doc.get("html_url", ""),
                    published=doc.get("publication_date", ""),
                    summary=abstract,
                    category_hint=category_hint,
                )
            )

        return FetchResult(
            source=self.name,
            fetched_at=datetime.now(timezone.utc).isoformat(),
            items=items,
        )
