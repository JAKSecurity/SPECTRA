from unittest.mock import patch, MagicMock

from src.collect.fetchers.congress_gov import CongressGovFetcher, _bill_url


MOCK_CONGRESS_RESPONSE = {
    "bills": [
        {
            "number": "1234",
            "title": "Federal Cybersecurity Workforce Expansion Act",
            "type": "HR",
            "congress": 119,
            "latestAction": {
                "text": "Referred to the Committee on Homeland Security.",
                "actionDate": "2026-04-01",
            },
            "url": "https://api.congress.gov/v3/bill/119/hr/1234",
        },
        {
            "number": "567",
            "title": "Securing Critical Infrastructure Act",
            "type": "S",
            "congress": 119,
            "latestAction": {
                "text": "Passed Senate by unanimous consent.",
                "actionDate": "2026-03-28",
            },
            "url": "https://api.congress.gov/v3/bill/119/s/567",
        },
    ],
}


class TestBillUrl:
    def test_house_bill(self):
        url = _bill_url(119, "HR", "1234")
        assert url == "https://www.congress.gov/bill/119th-congress/house-bill/1234"

    def test_senate_bill(self):
        url = _bill_url(119, "S", "567")
        assert url == "https://www.congress.gov/bill/119th-congress/senate-bill/567"


class TestCongressGovFetcher:
    def test_returns_empty_without_api_key(self):
        config = {"search_term": "cybersecurity", "category_hint": "legislative"}
        fetcher = CongressGovFetcher("congress_gov", config)

        with patch.dict("os.environ", {}, clear=True):
            result = fetcher.fetch()

        assert result.source == "congress_gov"
        assert len(result.items) == 0

    def test_fetches_bills_with_api_key(self):
        config = {"api_key": "test-key", "search_term": "cybersecurity", "category_hint": "legislative"}
        fetcher = CongressGovFetcher("congress_gov", config)

        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_CONGRESS_RESPONSE
        mock_resp.raise_for_status = MagicMock()

        with patch("src.collect.fetchers.congress_gov.requests.get", return_value=mock_resp):
            result = fetcher.fetch()

        assert len(result.items) == 2
        assert "HR 1234" in result.items[0].title
        assert "Cybersecurity Workforce" in result.items[0].title
        assert "house-bill/1234" in result.items[0].url

    def test_senate_bill_url(self):
        config = {"api_key": "test-key", "search_term": "cybersecurity", "category_hint": "legislative"}
        fetcher = CongressGovFetcher("congress_gov", config)

        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_CONGRESS_RESPONSE
        mock_resp.raise_for_status = MagicMock()

        with patch("src.collect.fetchers.congress_gov.requests.get", return_value=mock_resp):
            result = fetcher.fetch()

        assert "senate-bill/567" in result.items[1].url

    def test_includes_latest_action_in_summary(self):
        config = {"api_key": "test-key", "search_term": "cybersecurity", "category_hint": "legislative"}
        fetcher = CongressGovFetcher("congress_gov", config)

        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_CONGRESS_RESPONSE
        mock_resp.raise_for_status = MagicMock()

        with patch("src.collect.fetchers.congress_gov.requests.get", return_value=mock_resp):
            result = fetcher.fetch()

        assert "Referred to the Committee" in result.items[0].summary
        assert "2026-04-01" in result.items[0].summary

    def test_handles_empty_results(self):
        config = {"api_key": "test-key", "search_term": "cybersecurity", "category_hint": "legislative"}
        fetcher = CongressGovFetcher("congress_gov", config)

        mock_resp = MagicMock()
        mock_resp.json.return_value = {"bills": []}
        mock_resp.raise_for_status = MagicMock()

        with patch("src.collect.fetchers.congress_gov.requests.get", return_value=mock_resp):
            result = fetcher.fetch()

        assert len(result.items) == 0
