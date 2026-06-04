import hashlib
import os
from datetime import datetime, timezone, timedelta

import requests

from .base import BaseFetcher, FetchedItem, FetchResult
from .rss import _strip_html


def _bill_url(congress: int, bill_type: str, number: str) -> str:
    """Construct a congress.gov URL from bill metadata."""
    chamber = "senate" if bill_type.upper().startswith("S") else "house"
    return f"https://www.congress.gov/bill/{congress}th-congress/{chamber}-bill/{number}"


def _keyring_api_key() -> str:
    """Read the Congress.gov API key from the OS keyring (service 'spectra').

    Safe fallback: any failure (keyring missing, no entry, backend error) returns
    "" so collection degrades to an empty result instead of crashing -- matching
    the prior no-key behavior. Ticket 001."""
    try:
        import keyring

        return keyring.get_password("spectra", "CONGRESS_GOV_API_KEY") or ""
    except Exception:
        return ""


class CongressGovFetcher(BaseFetcher):
    def fetch(self) -> FetchResult:
        api_key = (
            self.config.get("api_key")
            or os.environ.get("CONGRESS_GOV_API_KEY", "")
            or _keyring_api_key()
        )
        search_term = self.config.get("search_term", "cybersecurity")
        days_back = self.config.get("days_back", 30)
        category_hint = self.config.get("category_hint", "legislative")

        if not api_key:
            return FetchResult(
                source=self.name,
                fetched_at=datetime.now(timezone.utc).isoformat(),
                items=[],
            )

        since = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00Z")

        resp = requests.get(
            "https://api.congress.gov/v3/bill",
            params={
                "query": search_term,
                "sort": "updateDate+desc",
                "limit": 20,
                "fromDateTime": since,
                "api_key": api_key,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        items = []
        for bill in data.get("bills", []):
            bill_type = bill.get("type", "HR")
            number = str(bill.get("number", ""))
            congress = bill.get("congress", 119)
            title = _strip_html(bill.get("title", ""))
            bill_id = f"{bill_type}{number}-{congress}"
            item_id = hashlib.sha256(bill_id.encode()).hexdigest()[:16]

            latest_action = bill.get("latestAction", {})
            action_text = latest_action.get("text", "")
            action_date = latest_action.get("actionDate", "")
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
