"""Offline response replay for tickets 003 (CISA retry) and 004 (Congress filtering)."""
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest
import requests
import yaml

from src.collect.fetchers.congress_gov import CongressGovFetcher
from src.collect.runner import run_collect

FIXTURES = Path(__file__).parent / "fixtures"


def response(filename, status=200):
    result = requests.Response()
    result.status_code = status
    result.url = "https://example.test/response"
    result._content = (FIXTURES / filename).read_bytes()
    return result


@pytest.mark.parametrize("first", ["empty-feed.xml", "unavailable.html", "http-error", "timeout"])
def test_cisa_retries_before_saving_health(tmp_path, first):
    config = tmp_path / "sources.yaml"
    config.write_text(yaml.safe_dump({"sources": {"cisa_alerts": {
        "type": "rss", "core": True,
        "url": "https://www.cisa.gov/cybersecurity-advisories/all.xml",
    }}}))
    initial = {
        "http-error": response("unavailable.html", 503),
        "timeout": requests.Timeout("Timed out"),
    }.get(first)
    if initial is None:
        initial = response(first)
    with patch("src.collect.fetchers.rss.requests.get", side_effect=[initial, response("cisa-alerts.xml")]) as get, patch("src.collect.runner.time.sleep") as sleep:
        results = run_collect(str(config), str(tmp_path / "sources"), "2026-11")
    assert results[0]["status"] == "ok"
    assert results[0]["items"] == 1
    assert get.call_count == 2
    assert all(call.kwargs["timeout"] == 30 for call in get.call_args_list)
    sleep.assert_called_once_with(1)
    health = json.loads((tmp_path / "sources/2026-11/_health.json").read_text())
    assert health["summary"]["empty"] == health["summary"]["failed"] == 0


@pytest.mark.parametrize("status, expected", [(200, "ok"), (503, "error")])
def test_cisa_retry_is_bounded_and_preserves_final_health(tmp_path, status, expected):
    config = tmp_path / "sources.yaml"
    config.write_text(yaml.safe_dump({"sources": {"cisa_alerts": {
        "type": "rss", "core": True, "url": "https://example.test/feed",
    }}}))
    with patch("src.collect.fetchers.rss.requests.get", return_value=response("empty-feed.xml", status)) as get, patch("src.collect.runner.time.sleep") as sleep:
        results = run_collect(str(config), str(tmp_path / "sources"), "2026-11")
    assert get.call_count == 2
    sleep.assert_called_once_with(1)
    assert results[0]["status"] == expected
    health = json.loads((tmp_path / "sources/2026-11/_health.json").read_text())
    assert health["warnings"]
    assert health["summary"]["empty" if status == 200 else "failed"] == 1


def congress_config(**overrides):
    return {
        "api_key": "test-placeholder", "search_terms": ["cybersecurity", "cyber security"],
        "start_date": "2026-10-01", "end_date": "2026-11-01", **overrides,
    }


def test_congress_relevance_window_pagination_and_header():
    with patch("src.collect.fetchers.congress_gov.requests.get", side_effect=[response("congress-page-1.json"), response("congress-page-2.json")]) as get:
        result = CongressGovFetcher("congress_gov", congress_config()).fetch()
    assert [item.title.split(" - ")[0] for item in result.items] == ["HR 3", "HR 4", "HR 7"]
    assert [item.published for item in result.items] == ["2026-10-01", "2026-10-31", "2026-10-20"]
    assert get.call_count == 2
    for index, call in enumerate(get.call_args_list):
        assert call.args == ("https://api.congress.gov/v3/bill",)
        assert call.kwargs["headers"] == {"X-Api-Key": "test-placeholder"}
        params = call.kwargs["params"]
        assert params == {
            "format": "json", "limit": 250, "offset": index * 250,
            "fromDateTime": "2026-10-01T00:00:00Z", "toDateTime": "2026-11-01T00:00:00Z",
        }


def test_congress_page_limit_does_not_silently_return_partial_results():
    with patch("src.collect.fetchers.congress_gov.requests.get", return_value=response("congress-page-1.json")) as get:
        with pytest.raises(RuntimeError, match="page limit.*incomplete"):
            CongressGovFetcher("congress_gov", congress_config(max_pages=2)).fetch()
    assert get.call_count == 2


def test_congress_days_back_applies_without_explicit_report_window():
    config = congress_config(days_back=30)
    config.pop("start_date")
    config.pop("end_date")
    with patch("src.collect.fetchers.congress_gov.datetime") as clock, patch("src.collect.fetchers.congress_gov.requests.get", return_value=response("congress-page-2.json")) as get:
        clock.now.return_value = datetime(2026, 10, 31, tzinfo=timezone.utc)
        clock.strptime.side_effect = datetime.strptime
        result = CongressGovFetcher("congress_gov", config).fetch()
    assert [item.published for item in result.items] == ["2026-10-31", "2026-10-20"]
    assert get.call_args.kwargs["params"]["fromDateTime"] == "2026-10-01T00:00:00Z"


def test_congress_terms_can_be_extended():
    with patch("src.collect.fetchers.congress_gov.requests.get", return_value=response("congress-page-2.json")):
        result = CongressGovFetcher("congress_gov", congress_config(search_terms=["FEDERAL SYSTEMS"])).fetch()
    assert len(result.items) == 1
    assert "HR 7" in result.items[0].title
