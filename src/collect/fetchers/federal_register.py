import hashlib
import logging
from datetime import datetime, timezone, timedelta

import requests

from .base import BaseFetcher, FetchedItem, FetchResult
from .rss import _strip_html


logger = logging.getLogger(__name__)
MAX_PAGES = 10


class FederalRegisterFetcher(BaseFetcher):
    def fetch(self) -> FetchResult:
        search_term = self.config.get("search_term", "cybersecurity")
        days_back = self.config.get("days_back", 30)
        category_hint = self.config.get("category_hint", "policy")

        since = self.config.get("start_date") or (
            datetime.now(timezone.utc) - timedelta(days=days_back)
        ).strftime("%Y-%m-%d")
        before = self.config.get("end_date")

        url = "https://www.federalregister.gov/api/v1/documents.json"
        params = {
            "conditions[term]": search_term,
            "conditions[publication_date][gte]": since,
            **({"conditions[publication_date][lt]": before} if before else {}),
            "per_page": 50,
            "order": "newest",
            "fields[]": ["title", "abstract", "html_url", "publication_date", "document_number", "type"],
        }
        items = []
        seen = set()
        pages_fetched = 0
        page_cap_reached = False
        for _ in range(MAX_PAGES):
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            pages_fetched += 1

            for doc in data.get("results", []):
                document_number = doc.get("document_number")
                if document_number is not None:
                    if document_number in seen:
                        continue
                    seen.add(document_number)
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

            url = data.get("next_page_url")
            if not url:
                break
            # The API continuation URL already carries the original query parameters.
            params = None
        else:
            page_cap_reached = True
            logger.warning(
                "Federal Register collection reached the %s-page cap; "
                "more results remain and collection is incomplete",
                MAX_PAGES,
            )

        return FetchResult(
            source=self.name,
            fetched_at=datetime.now(timezone.utc).isoformat(),
            items=items,
            pages_fetched=pages_fetched,
            page_cap_reached=page_cap_reached,
            # Publication-date query bounds cover the requested window server-side.
            window_start_reached=True,
        )
