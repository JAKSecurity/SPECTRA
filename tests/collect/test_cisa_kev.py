from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta

from src.collect.fetchers.cisa_kev import CISAKEVFetcher


def _recent_date(days_ago=5):
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime("%Y-%m-%d")


def _old_date():
    return (datetime.now(timezone.utc) - timedelta(days=60)).strftime("%Y-%m-%d")


MOCK_KEV_RESPONSE = {
    "title": "CISA KEV Catalog",
    "catalogVersion": "2026.04.07",
    "vulnerabilities": [
        {
            "cveID": "CVE-2026-1234",
            "vendorProject": "Microsoft",
            "product": "Windows",
            "vulnerabilityName": "Microsoft Windows Kernel Privilege Escalation",
            "dateAdded": _recent_date(5),
            "shortDescription": "A privilege escalation vulnerability in Windows kernel.",
            "dueDate": _recent_date(-14),
        },
        {
            "cveID": "CVE-2026-5678",
            "vendorProject": "Apache",
            "product": "HTTP Server",
            "vulnerabilityName": "Apache HTTP Server Path Traversal",
            "dateAdded": _recent_date(10),
            "shortDescription": "A path traversal vulnerability in Apache HTTP Server.",
            "dueDate": _recent_date(-7),
        },
        {
            "cveID": "CVE-2025-9999",
            "vendorProject": "Old Vendor",
            "product": "Old Product",
            "vulnerabilityName": "Old Vulnerability",
            "dateAdded": _old_date(),
            "shortDescription": "An old vulnerability outside the window.",
            "dueDate": "2025-12-01",
        },
    ],
}


class TestCISAKEVFetcher:
    def test_fetches_recent_vulnerabilities(self):
        config = {"days_back": 30, "category_hint": "threats"}
        fetcher = CISAKEVFetcher("cisa_kev", config)

        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_KEV_RESPONSE
        mock_resp.raise_for_status = MagicMock()

        with patch("src.collect.fetchers.cisa_kev.requests.get", return_value=mock_resp):
            result = fetcher.fetch()

        assert result.source == "cisa_kev"
        assert len(result.items) == 2  # Old one should be filtered out
        assert "CVE-2026-1234" in result.items[0].title

    def test_filters_old_entries(self):
        config = {"days_back": 30, "category_hint": "threats"}
        fetcher = CISAKEVFetcher("cisa_kev", config)

        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_KEV_RESPONSE
        mock_resp.raise_for_status = MagicMock()

        with patch("src.collect.fetchers.cisa_kev.requests.get", return_value=mock_resp):
            result = fetcher.fetch()

        titles = [item.title for item in result.items]
        assert not any("CVE-2025-9999" in t for t in titles)

    def test_includes_due_date_in_summary(self):
        config = {"days_back": 30, "category_hint": "threats"}
        fetcher = CISAKEVFetcher("cisa_kev", config)

        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_KEV_RESPONSE
        mock_resp.raise_for_status = MagicMock()

        with patch("src.collect.fetchers.cisa_kev.requests.get", return_value=mock_resp):
            result = fetcher.fetch()

        assert "Remediation due by" in result.items[0].summary

    def test_links_to_nvd(self):
        config = {"days_back": 30, "category_hint": "threats"}
        fetcher = CISAKEVFetcher("cisa_kev", config)

        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_KEV_RESPONSE
        mock_resp.raise_for_status = MagicMock()

        with patch("src.collect.fetchers.cisa_kev.requests.get", return_value=mock_resp):
            result = fetcher.fetch()

        assert "nvd.nist.gov/vuln/detail/CVE-2026-1234" in result.items[0].url

    def test_handles_empty_catalog(self):
        config = {"days_back": 30, "category_hint": "threats"}
        fetcher = CISAKEVFetcher("cisa_kev", config)

        mock_resp = MagicMock()
        mock_resp.json.return_value = {"vulnerabilities": []}
        mock_resp.raise_for_status = MagicMock()

        with patch("src.collect.fetchers.cisa_kev.requests.get", return_value=mock_resp):
            result = fetcher.fetch()

        assert len(result.items) == 0
