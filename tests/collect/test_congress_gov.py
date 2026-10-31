from unittest.mock import patch, MagicMock

import pytest

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
            "title": "Cybersecurity and Critical Infrastructure Act",
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
    @pytest.mark.parametrize("bill_type, path", [
        ("HR", "house-bill"),
        ("S", "senate-bill"),
        ("HRES", "house-resolution"),
        ("SRES", "senate-resolution"),
        ("HCONRES", "house-concurrent-resolution"),
        ("SCONRES", "senate-concurrent-resolution"),
        ("HJRES", "house-joint-resolution"),
        ("SJRES", "senate-joint-resolution"),
    ])
    def test_measure_type(self, bill_type, path):
        assert _bill_url(119, bill_type, "1") == (
            f"https://www.congress.gov/bill/119th-congress/{path}/1"
        )

    def test_lowercase_type(self):
        assert _bill_url(119, "hjres", "1") == (
            "https://www.congress.gov/bill/119th-congress/house-joint-resolution/1"
        )

    def test_unknown_type_uses_search_and_logs(self, caplog):
        assert _bill_url(119, "UNKNOWN", "1234") == (
            "https://www.congress.gov/search?q=1234"
        )
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.name == "src.collect.fetchers.congress_gov"
        assert record.levelname == "WARNING"
        assert "UNKNOWN" in record.message
        assert "search" in record.message

    def test_search_number_is_encoded(self):
        assert _bill_url(119, "UNKNOWN", "12&34") == (
            "https://www.congress.gov/search?q=12%2634"
        )

    @pytest.mark.parametrize("congress, ordinal", [
        (119, "119th"), (121, "121st"), (122, "122nd"),
        (123, "123rd"), (111, "111th"), (112, "112th"), (113, "113th"),
    ])
    def test_congress_ordinal(self, congress, ordinal):
        assert _bill_url(congress, "HR", "1") == (
            f"https://www.congress.gov/bill/{ordinal}-congress/house-bill/1"
        )

    def test_house_bill(self):
        url = _bill_url(119, "HR", "1234")
        assert url == "https://www.congress.gov/bill/119th-congress/house-bill/1234"

    def test_senate_bill(self):
        url = _bill_url(119, "S", "567")
        assert url == "https://www.congress.gov/bill/119th-congress/senate-bill/567"


class TestCongressGovFetcher:
    def test_returns_unavailable_without_api_key(self):
        config = {"search_term": "cybersecurity", "category_hint": "legislative"}
        fetcher = CongressGovFetcher("congress_gov", config)

        # Clear env AND the keyring fallback so the test reflects "no key anywhere"
        # regardless of what is provisioned on the machine running the suite.
        with patch.dict("os.environ", {}, clear=True), patch(
            "src.collect.fetchers.congress_gov._keyring_api_key", return_value=""
        ):
            result = fetcher.fetch()

        assert result.source == "congress_gov"
        assert result.status == "unavailable"
        assert len(result.items) == 0

    def test_fetches_bills_with_api_key(self):
        config = {"api_key": "test-key", "search_term": "cybersecurity", "category_hint": "legislative", "start_date": "2026-03-01", "end_date": "2026-05-01"}
        fetcher = CongressGovFetcher("congress_gov", config)

        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_CONGRESS_RESPONSE
        mock_resp.status_code = 200

        with patch("src.collect.fetchers.congress_gov.requests.get", return_value=mock_resp):
            result = fetcher.fetch()

        assert len(result.items) == 2
        assert "HR 1234" in result.items[0].title
        assert "Cybersecurity Workforce" in result.items[0].title
        assert "house-bill/1234" in result.items[0].url

    def test_senate_bill_url(self):
        config = {"api_key": "test-key", "search_term": "cybersecurity", "category_hint": "legislative", "start_date": "2026-03-01", "end_date": "2026-05-01"}
        fetcher = CongressGovFetcher("congress_gov", config)

        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_CONGRESS_RESPONSE
        mock_resp.status_code = 200

        with patch("src.collect.fetchers.congress_gov.requests.get", return_value=mock_resp):
            result = fetcher.fetch()

        assert "senate-bill/567" in result.items[1].url

    def test_includes_latest_action_in_summary(self):
        config = {"api_key": "test-key", "search_term": "cybersecurity", "category_hint": "legislative", "start_date": "2026-03-01", "end_date": "2026-05-01"}
        fetcher = CongressGovFetcher("congress_gov", config)

        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_CONGRESS_RESPONSE
        mock_resp.status_code = 200

        with patch("src.collect.fetchers.congress_gov.requests.get", return_value=mock_resp):
            result = fetcher.fetch()

        assert "Referred to the Committee" in result.items[0].summary
        assert "2026-04-01" in result.items[0].summary

    def test_handles_empty_results(self):
        config = {"api_key": "test-key", "search_term": "cybersecurity", "category_hint": "legislative", "start_date": "2026-03-01", "end_date": "2026-05-01"}
        fetcher = CongressGovFetcher("congress_gov", config)

        mock_resp = MagicMock()
        mock_resp.json.return_value = {"bills": []}
        mock_resp.status_code = 200

        with patch("src.collect.fetchers.congress_gov.requests.get", return_value=mock_resp):
            result = fetcher.fetch()

        assert len(result.items) == 0

    def test_filters_to_explicit_content_window(self):
        config = {
            "api_key": "test-key",
            "search_term": "cybersecurity",
            "start_date": "2026-04-01",
            "end_date": "2026-05-01",
        }
        fetcher = CongressGovFetcher("congress_gov", config)
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_CONGRESS_RESPONSE
        mock_resp.status_code = 200

        with patch("src.collect.fetchers.congress_gov.requests.get", return_value=mock_resp) as mock_get:
            result = fetcher.fetch()

        assert [item.published for item in result.items] == ["2026-04-01"]
        params = mock_get.call_args.kwargs["params"]
        assert params["fromDateTime"] == "2026-04-01T00:00:00Z"
        assert params["toDateTime"] == "2026-05-01T00:00:00Z"

    def test_error_response_does_not_leak_api_key(self):
        # Security: an HTTP error must NOT surface the api_key. raise_for_status()
        # would embed the request URL (with ?api_key=...) in the exception; the
        # fetcher must raise a scrubbed error instead. Ticket 001.
        import pytest

        secret = "SUPERSECRETKEY12345"
        config = {"api_key": secret, "search_term": "cybersecurity", "category_hint": "legislative"}
        fetcher = CongressGovFetcher("congress_gov", config)

        mock_resp = MagicMock()
        mock_resp.status_code = 403

        with patch("src.collect.fetchers.congress_gov.requests.get", return_value=mock_resp):
            with pytest.raises(Exception) as exc_info:
                fetcher.fetch()

        assert secret not in str(exc_info.value)
        assert "403" in str(exc_info.value)


@pytest.mark.parametrize("origin, api_key", [
    (origin, key)
    for origin in ("config", "environment", "keyring")
    for key in (
        " FAKE-KEY-123", "FAKE-KEY-123 ", "FAKE-KEY-123\nTAIL",
        "FAKE-KEY-123\tTAIL", "FAKE-KEY-123\x00TAIL", "FAKE-KEY-123\x7fTAIL",
        "FAKE-KEY-123\x85TAIL",
    )
    # Linux environment variables cannot contain null bytes.
    if not (origin == "environment" and "\x00" in key)
])
def test_malformed_key_is_rejected_before_request(api_key, origin, monkeypatch):
    config = {"api_key": api_key} if origin == "config" else {}
    monkeypatch.setenv("CONGRESS_GOV_API_KEY", api_key if origin == "environment" else "")
    with patch("src.collect.fetchers.congress_gov._keyring_api_key",
               return_value=api_key if origin == "keyring" else ""), patch(
        "src.collect.fetchers.congress_gov.requests.get"
    ) as get:
        with pytest.raises(ValueError, match="^Congress.gov API key is malformed$"):
            CongressGovFetcher("congress_gov", config).fetch()
    get.assert_not_called()


def test_well_formed_key_preserves_request_result_and_messages(caplog, capsys):
    response = MagicMock(status_code=200)
    response.json.return_value = MOCK_CONGRESS_RESPONSE
    config = {
        "api_key": "FAKE-KEY-123", "start_date": "2026-03-01",
        "end_date": "2026-05-01",
    }
    with patch("src.collect.fetchers.congress_gov.requests.get", return_value=response) as get:
        result = CongressGovFetcher("congress_gov", config).fetch()
    get.assert_called_once_with(
        "https://api.congress.gov/v3/bill",
        params={"format": "json", "limit": 250, "offset": 0,
                "fromDateTime": "2026-03-01T00:00:00Z", "toDateTime": "2026-05-01T00:00:00Z"},
        headers={"X-Api-Key": "FAKE-KEY-123"}, timeout=30,
    )
    assert result.status == "ok"
    assert [item.title for item in result.items] == [
        "HR 1234 - Federal Cybersecurity Workforce Expansion Act",
        "S 567 - Cybersecurity and Critical Infrastructure Act",
    ]
    assert result.pages_fetched == 1
    assert result.page_cap_reached is False
    assert result.window_start_reached is None
    assert not caplog.records
    captured = capsys.readouterr()
    assert captured.out == captured.err == ""
