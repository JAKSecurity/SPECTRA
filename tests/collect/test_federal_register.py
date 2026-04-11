import json
from unittest.mock import patch, MagicMock

from src.collect.fetchers.federal_register import FederalRegisterFetcher


MOCK_FR_RESPONSE = {
    "count": 2,
    "results": [
        {
            "title": "Cybersecurity Maturity Model Certification Program",
            "abstract": "<p>The Department of Defense is amending the DFARS to implement CMMC requirements.</p>",
            "html_url": "https://www.federalregister.gov/documents/2026/04/01/2026-12345/cmmc",
            "publication_date": "2026-04-01",
            "document_number": "2026-12345",
            "type": "Rule",
        },
        {
            "title": "Cybersecurity Incident Reporting for Critical Infrastructure",
            "abstract": "CISA proposes reporting requirements under CIRCIA.",
            "html_url": "https://www.federalregister.gov/documents/2026/03/28/2026-67890/circia",
            "publication_date": "2026-03-28",
            "document_number": "2026-67890",
            "type": "Proposed Rule",
        },
    ],
}


class TestFederalRegisterFetcher:
    def test_fetches_and_parses_documents(self):
        config = {"search_term": "cybersecurity", "category_hint": "policy"}
        fetcher = FederalRegisterFetcher("federal_register", config)

        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_FR_RESPONSE
        mock_resp.raise_for_status = MagicMock()

        with patch("src.collect.fetchers.federal_register.requests.get", return_value=mock_resp):
            result = fetcher.fetch()

        assert result.source == "federal_register"
        assert len(result.items) == 2
        assert result.items[0].title == "Cybersecurity Maturity Model Certification Program"
        assert result.items[0].published == "2026-04-01"
        assert "federalregister.gov" in result.items[0].url

    def test_strips_html_from_abstract(self):
        config = {"search_term": "cybersecurity", "category_hint": "policy"}
        fetcher = FederalRegisterFetcher("federal_register", config)

        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_FR_RESPONSE
        mock_resp.raise_for_status = MagicMock()

        with patch("src.collect.fetchers.federal_register.requests.get", return_value=mock_resp):
            result = fetcher.fetch()

        # First item has HTML in abstract
        assert "<p>" not in result.items[0].summary
        assert "CMMC" in result.items[0].summary

    def test_handles_empty_results(self):
        config = {"search_term": "cybersecurity", "category_hint": "policy"}
        fetcher = FederalRegisterFetcher("federal_register", config)

        mock_resp = MagicMock()
        mock_resp.json.return_value = {"count": 0, "results": []}
        mock_resp.raise_for_status = MagicMock()

        with patch("src.collect.fetchers.federal_register.requests.get", return_value=mock_resp):
            result = fetcher.fetch()

        assert len(result.items) == 0

    def test_generates_stable_ids(self):
        config = {"search_term": "cybersecurity", "category_hint": "policy"}
        fetcher = FederalRegisterFetcher("federal_register", config)

        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_FR_RESPONSE
        mock_resp.raise_for_status = MagicMock()

        with patch("src.collect.fetchers.federal_register.requests.get", return_value=mock_resp):
            result1 = fetcher.fetch()

        mock_resp2 = MagicMock()
        mock_resp2.json.return_value = MOCK_FR_RESPONSE
        mock_resp2.raise_for_status = MagicMock()

        with patch("src.collect.fetchers.federal_register.requests.get", return_value=mock_resp2):
            result2 = fetcher.fetch()

        assert result1.items[0].id == result2.items[0].id
        assert result1.items[0].id != result1.items[1].id
