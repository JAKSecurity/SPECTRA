import hashlib
from datetime import datetime, timezone, timedelta

import requests

from .base import BaseFetcher, FetchedItem, FetchResult


class CISAKEVFetcher(BaseFetcher):
    def fetch(self) -> FetchResult:
        days_back = self.config.get("days_back", 30)
        category_hint = self.config.get("category_hint", "threats")

        cutoff = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%d")

        resp = requests.get(
            "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        items = []
        for vuln in data.get("vulnerabilities", []):
            date_added = vuln.get("dateAdded", "")
            if date_added < cutoff:
                continue

            cve_id = vuln.get("cveID", "")
            item_id = hashlib.sha256(cve_id.encode()).hexdigest()[:16]
            vendor = vuln.get("vendorProject", "")
            product = vuln.get("product", "")
            title = f"{cve_id}: {vuln.get('vulnerabilityName', '')}"
            due = vuln.get("dueDate", "")
            summary = vuln.get("shortDescription", "")
            if due:
                summary += f" Remediation due by {due}."

            items.append(
                FetchedItem(
                    id=item_id,
                    title=title,
                    url=f"https://nvd.nist.gov/vuln/detail/{cve_id}",
                    published=date_added,
                    summary=summary,
                    category_hint=category_hint,
                )
            )

        return FetchResult(
            source=self.name,
            fetched_at=datetime.now(timezone.utc).isoformat(),
            items=items,
        )
