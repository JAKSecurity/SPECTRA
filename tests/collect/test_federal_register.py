from unittest.mock import patch, MagicMock
from urllib.parse import parse_qs, urlsplit

from src.collect.fetchers.federal_register import FederalRegisterFetcher


MOCK_FR_RESPONSE = {
    "count": 2,
    "total_pages": 1,
    "next_page_url": None,
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

    def test_uses_explicit_content_window(self):
        config = {
            "search_term": "cybersecurity",
            "start_date": "2026-03-01",
            "end_date": "2026-04-01",
        }
        fetcher = FederalRegisterFetcher("federal_register", config)
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"results": []}
        mock_resp.raise_for_status = MagicMock()

        with patch("src.collect.fetchers.federal_register.requests.get", return_value=mock_resp) as mock_get:
            fetcher.fetch()

        params = mock_get.call_args.kwargs["params"]
        assert params["conditions[publication_date][gte]"] == "2026-03-01"
        assert params["conditions[publication_date][lt]"] == "2026-04-01"

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

    def test_collects_two_pages(self):
        fetcher = FederalRegisterFetcher("federal_register", {
            "start_date": "2026-03-01", "end_date": "2026-04-01",
        })
        next_url = (
            "https://www.federalregister.gov/api/v1/documents.json?"
            "conditions%5Bterm%5D=cybersecurity&"
            "conditions%5Bpublication_date%5D%5Bgte%5D=2026-03-01&"
            "conditions%5Bpublication_date%5D%5Blt%5D=2026-04-01&"
            "per_page=50&order=newest&fields%5B%5D=title&"
            "fields%5B%5D=abstract&fields%5B%5D=html_url&"
            "fields%5B%5D=publication_date&fields%5B%5D=document_number&"
            "fields%5B%5D=type&page=2"
        )
        pages = [
            {"count": 2, "total_pages": 2, "next_page_url": next_url,
             "results": MOCK_FR_RESPONSE["results"][:1]},
            {"count": 2, "total_pages": 2, "next_page_url": None,
             "results": MOCK_FR_RESPONSE["results"][1:]},
        ]
        responses = [MagicMock() for _ in pages]
        for response, page in zip(responses, pages):
            response.json.return_value = page

        with patch("src.collect.fetchers.federal_register.requests.get",
                   side_effect=responses) as mock_get:
            result = fetcher.fetch()

        assert [item.title for item in result.items] == [
            doc["title"] for doc in MOCK_FR_RESPONSE["results"]
        ]
        assert mock_get.call_count == 2
        assert mock_get.call_args_list[1].args == (next_url,)
        assert mock_get.call_args_list[1].kwargs["params"] is None
        continuation_params = parse_qs(urlsplit(next_url).query)
        assert continuation_params.pop("page") == ["2"]
        assert continuation_params == {
            key: value if isinstance(value, list) else [str(value)]
            for key, value in mock_get.call_args_list[0].kwargs["params"].items()
        }
        assert all(call.kwargs["timeout"] == 30 for call in mock_get.call_args_list)
        for response in responses:
            response.raise_for_status.assert_called_once_with()

    def test_stops_after_single_page(self, caplog):
        fetcher = FederalRegisterFetcher("federal_register", {})
        response = MagicMock()
        response.json.return_value = MOCK_FR_RESPONSE

        with patch("src.collect.fetchers.federal_register.requests.get",
                   return_value=response) as mock_get:
            result = fetcher.fetch()

        assert len(result.items) == 2
        mock_get.assert_called_once()
        assert not caplog.records

    def test_page_cap_stops_and_warns(self, caplog):
        fetcher = FederalRegisterFetcher("federal_register", {})
        response = MagicMock()
        response.json.return_value = {
            "count": 11, "total_pages": 11,
            "next_page_url": "https://www.federalregister.gov/api/v1/documents.json?page=2",
            "results": MOCK_FR_RESPONSE["results"][:1],
        }
        with patch("src.collect.fetchers.federal_register.requests.get",
                   return_value=response) as mock_get:
            result = fetcher.fetch()

        assert mock_get.call_count == 10
        assert len(result.items) == 1
        assert any(record.levelname == "WARNING" and "10" in record.message
                   and "page" in record.message for record in caplog.records)

    def test_deduplicates_document_numbers_across_pages(self):
        fetcher = FederalRegisterFetcher("federal_register", {})
        responses = [MagicMock(), MagicMock()]
        responses[0].json.return_value = {
            "next_page_url": "https://www.federalregister.gov/api/v1/documents.json?page=2",
            "results": MOCK_FR_RESPONSE["results"][:1],
        }
        responses[1].json.return_value = {
            "next_page_url": None, "results": MOCK_FR_RESPONSE["results"],
        }
        with patch("src.collect.fetchers.federal_register.requests.get",
                   side_effect=responses) as mock_get:
            result = fetcher.fetch()

        assert mock_get.call_count == 2
        assert len(result.items) == 2
        assert len({item.id for item in result.items}) == 2


    def test_last_page_at_cap_does_not_warn(self, caplog):
        fetcher = FederalRegisterFetcher("federal_register", {})
        responses = [MagicMock() for _ in range(10)]
        for index, response in enumerate(responses):
            response.json.return_value = {
                "next_page_url": (
                    f"https://www.federalregister.gov/api/v1/documents.json?page={index + 2}"
                    if index < 9 else None
                ),
                "results": [],
            }
        with patch("src.collect.fetchers.federal_register.requests.get",
                   side_effect=responses) as mock_get:
            fetcher.fetch()

        assert mock_get.call_count == 10
        assert not caplog.records
