import hashlib
import logging
import os
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode

import requests

from .base import BaseFetcher, FetchedItem, FetchResult
from .rss import _strip_html


logger = logging.getLogger(__name__)

_MEASURE_PATHS = {
    "HR": "house-bill",
    "S": "senate-bill",
    "HRES": "house-resolution",
    "SRES": "senate-resolution",
    "HCONRES": "house-concurrent-resolution",
    "SCONRES": "senate-concurrent-resolution",
    "HJRES": "house-joint-resolution",
    "SJRES": "senate-joint-resolution",
}


def _ordinal(number: int) -> str:
    """Format a congress number with its English ordinal suffix."""
    suffix = (
        "th" if 11 <= number % 100 <= 13
        else {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    )
    return f"{number}{suffix}"


def _bill_url(congress: int, bill_type: str, number: str) -> str:
    """Construct a congress.gov measure URL, or search for unknown types."""
    path = _MEASURE_PATHS.get(bill_type.upper())
    if path is None:
        # WHY: Guessing a chamber's bill path can link to a different measure (201).
        logger.warning("Unknown Congress.gov measure type %r; falling back to search", bill_type)
        return f"https://www.congress.gov/search?{urlencode({'q': number})}"
    return f"https://www.congress.gov/bill/{_ordinal(congress)}-congress/{path}/{number}"


def _keyring_api_key() -> str:
    """Read the Congress.gov API key from the OS keyring.

    Uses the shared 'ai-assistant' keyring service (the same namespace
    scripts/secret_store.py provisions, so the standard vault tooling manages
    this key). Safe fallback: any failure (keyring missing, no entry, backend
    error) returns "" so collection degrades to an empty result instead of
    crashing -- matching the prior no-key behavior. Ticket 001."""
    try:
        import keyring

        return keyring.get_password("ai-assistant", "CONGRESS_GOV_API_KEY") or ""
    except Exception:
        return ""


class CongressGovFetcher(BaseFetcher):
    def fetch(self) -> FetchResult:
        api_key = (
            self.config.get("api_key")
            or os.environ.get("CONGRESS_GOV_API_KEY", "")
            or _keyring_api_key()
        )
        terms = self.config.get("search_terms", self.config.get("search_term", "cybersecurity"))
        if isinstance(terms, str):  # Backward-compatible with existing source configs.
            terms = [terms]
        terms = [term.strip().casefold() for term in terms if term.strip()]
        if not terms:
            raise ValueError("congress_gov requires at least one search term")
        max_pages = int(self.config.get("max_pages", 40))
        if not 1 <= max_pages <= 40:
            raise ValueError("congress_gov max_pages must be between 1 and 40")
        days_back = self.config.get("days_back", 30)
        category_hint = self.config.get("category_hint", "legislative")

        if not api_key:
            return FetchResult(
                source=self.name,
                fetched_at=datetime.now(timezone.utc).isoformat(),
                items=[],
            )

        now = datetime.now(timezone.utc)
        start_date = self.config.get("start_date") or (now - timedelta(days=days_back)).date().isoformat()
        end_date = self.config.get("end_date") or (now + timedelta(days=1)).date().isoformat()

        # WHY: /bill has no keyword query parameter, and its date parameters filter
        # updates, not legislative action dates. Filter relevance/actions locally (004).
        # https://api.congress.gov/ and LibraryOfCongress/api.congress.gov Documentation/BillEndpoint.md
        bills = []
        seen = set()
        for page in range(max_pages):
            resp = requests.get(
                "https://api.congress.gov/v3/bill",
                params={
                    "format": "json",
                    "limit": 250,
                    "offset": page * 250,
                    "fromDateTime": f"{start_date}T00:00:00Z",
                    "toDateTime": f"{end_date}T00:00:00Z",
                },
                headers={"X-Api-Key": api_key},
                timeout=30,
            )
            if resp.status_code != 200:
                raise RuntimeError(f"congress_gov API error: HTTP {resp.status_code}")
            data = resp.json()
            for bill in data.get("bills", []):
                identity = (bill.get("congress"), bill.get("type"), bill.get("number"))
                if identity not in seen:
                    seen.add(identity)
                    bills.append(bill)
            # Do not follow the supplied URL: it can contain an API key. Build our
            # own offsets with header authentication and exhaust the update window.
            if not data.get("pagination", {}).get("next"):
                break
        else:
            raise RuntimeError("congress_gov page limit reached; report window incomplete")

        items = []
        for bill in bills:
            bill_type = bill.get("type", "HR")
            number = str(bill.get("number", ""))
            congress = bill.get("congress", 119)
            title = _strip_html(bill.get("title", ""))
            bill_id = f"{bill_type}{number}-{congress}"
            item_id = hashlib.sha256(bill_id.encode()).hexdigest()[:16]

            latest_action = bill.get("latestAction", {})
            action_text = latest_action.get("text", "")
            action_date = latest_action.get("actionDate", "")
            if not any(term in f"{title} {action_text}".casefold() for term in terms):
                continue
            try:
                datetime.strptime(action_date, "%Y-%m-%d")
            except (ValueError, TypeError):
                continue
            if action_date < start_date:
                continue
            if action_date >= end_date:
                continue
            summary = f"{bill_type} {number}: {title}"
            if action_text:
                summary += f" Latest action ({action_date}): {action_text}"

            url = _bill_url(congress, bill_type, number)

            items.append(
                FetchedItem(
                    id=item_id,
                    title=f"{bill_type} {number} - {title}",
                    url=url,
                    published=action_date,
                    summary=summary,
                    category_hint=category_hint,
                )
            )

        return FetchResult(
            source=self.name,
            fetched_at=datetime.now(timezone.utc).isoformat(),
            items=items,
        )
