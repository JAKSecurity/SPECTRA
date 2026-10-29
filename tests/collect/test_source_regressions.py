"""Offline response replay for source retries, filtering, and feed history."""
from copy import deepcopy
import hashlib
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest
import requests
import yaml

from src.collect.fetchers.congress_gov import CongressGovFetcher
from src.collect.fetchers.rss import RSSFetcher, USER_AGENT
from src.collect.runner import run_collect

FIXTURES = Path(__file__).parent / "fixtures"


def rss_config(**overrides):
    return {
        "url": "https://example.test/feed/?topic=security",
        "paged": True, "max_pages": 5,
        "start_date": "2026-10-01", "end_date": "2026-11-01", **overrides,
    }


@pytest.mark.parametrize("stop", ["empty", "older", "404"])
def test_rss_paging_stops_and_deduplicates(stop, caplog):
    last = {
        "empty": response("empty-feed.xml"),
        "older": response("wordpress-page-3.xml"),
        "404": response("unavailable.html", 404),
    }[stop]
    with patch("src.collect.fetchers.rss.requests.get", side_effect=[
        response("wordpress-page-1.xml"), response("wordpress-page-2.xml"), last,
    ]) as get:
        result = RSSFetcher("test", rss_config()).fetch()
    assert [item.published for item in result.items] == ["2026-10-28", "2026-10-27", "2026-10-01"]
    assert len({item.id for item in result.items}) == 3
    assert result.pages_fetched == (2 if stop == "404" else 3)
    assert result.page_cap_reached is False
    assert result.window_start_reached is True
    assert [call.args[0] for call in get.call_args_list] == [
        "https://example.test/feed/?topic=security",
        "https://example.test/feed/?topic=security&paged=2",
        "https://example.test/feed/?topic=security&paged=3",
    ]
    for call in get.call_args_list:
        assert call.kwargs == {"headers": {"User-Agent": USER_AGENT}, "timeout": 30}
    assert not caplog.records


@pytest.mark.parametrize("limit, expected", [(None, 1), (2, 2), (50, 10), (0, 1)])
def test_rss_paging_warns_at_bounded_cap(limit, expected, caplog):
    config = rss_config()
    if limit is None:
        config.pop("max_pages")
    else:
        config["max_pages"] = limit
    with patch("src.collect.fetchers.rss.requests.get", return_value=response("wordpress-page-1.xml")) as get:
        result = RSSFetcher("test", config).fetch()
    assert get.call_count == expected
    assert len(result.items) == 2
    assert result.pages_fetched == expected
    assert result.page_cap_reached is True
    assert result.window_start_reached is False
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "WARNING"
    assert f"page cap ({expected})" in caplog.text


@pytest.mark.parametrize("paged", [None, False])
def test_rss_without_paging_makes_one_identified_request(paged, caplog):
    config = rss_config()
    if paged is None:
        config.pop("paged")
    else:
        config["paged"] = paged
    with patch("src.collect.fetchers.rss.requests.get", return_value=response("wordpress-page-1.xml")) as get:
        assert len(RSSFetcher("test", config).fetch().items) == 2
    get.assert_called_once_with(config["url"], headers={"User-Agent": USER_AGENT}, timeout=30)
    assert USER_AGENT == "SPECTRA-monthly-report/1.0 (+https://github.com/JAKSecurity/SPECTRA)"
    assert not caplog.records


@pytest.mark.parametrize("status, paged", [(404, True), (403, True), (503, True), (404, False)])
def test_rss_first_page_errors_still_raise(status, paged):
    with patch("src.collect.fetchers.rss.requests.get", return_value=response("unavailable.html", status)) as get:
        with pytest.raises(requests.HTTPError):
            RSSFetcher("test", rss_config(paged=paged)).fetch()
    assert get.call_count == 1


def test_rss_later_page_non_404_error_still_raises():
    with patch("src.collect.fetchers.rss.requests.get", side_effect=[
        response("wordpress-page-1.xml"), response("unavailable.html", 403),
    ]) as get:
        with pytest.raises(requests.HTTPError):
            RSSFetcher("test", rss_config()).fetch()
    assert get.call_count == 2


def test_rss_undated_page_does_not_stop_paging():
    undated = response("wordpress-page-3.xml")
    undated._content = undated.content.replace(
        b"<pubDate>Wed, 30 Sep 2026 12:00:00 +0000</pubDate>", b""
    )
    with patch("src.collect.fetchers.rss.requests.get", side_effect=[
        undated, response("wordpress-page-1.xml"), response("empty-feed.xml"),
    ]) as get:
        result = RSSFetcher("test", rss_config()).fetch()
    assert get.call_count == 3
    assert len(result.items) == 2


def test_only_verified_sources_opt_into_rss_paging():
    config_path = Path(__file__).parents[2] / "src/collect/config.yaml"
    sources = yaml.safe_load(config_path.read_text())["sources"]
    assert {name: config["max_pages"] for name, config in sources.items()
            if config.get("paged")} == {"cyberscoop": 10, "mit_tech_review_ai": 6}


@pytest.mark.parametrize("name, boundary_page, count, earliest", [
    ("cyberscoop", 8, 14, "2026-10-01"),
    ("mit_tech_review_ai", 4, 6, "2026-10-02"),
])
def test_live_history_shapes_stop_at_window_and_deduplicate_identity(
    name, boundary_page, count, earliest, caplog,
):
    config_path = Path(__file__).parents[2] / "src/collect/config.yaml"
    config = yaml.safe_load(config_path.read_text())["sources"][name]
    config.update(start_date="2026-10-01", end_date="2026-11-01")
    assert config["max_pages"] > boundary_page
    pages = [response(f"{name}-history-page-{page}.xml")
             for page in range(1, boundary_page + 1)]
    # Replay an overlap with a changed reader URL: the publisher GUID owns identity.
    first_channel = ET.fromstring(pages[0].content).find("channel")
    duplicate = deepcopy(first_channel.findall("item")[-1])
    identity = duplicate.findtext("guid")
    duplicate.find("link").text = "https://example.test/changed-reader-url"
    second = ET.fromstring(pages[1].content)
    second.find("channel").append(duplicate)
    pages[1]._content = ET.tostring(second)
    with patch("src.collect.fetchers.rss.requests.get", side_effect=pages) as get:
        result = RSSFetcher(name, config).fetch()
    assert get.call_count == boundary_page  # No request for the configured margin pages.
    assert [call.args[0] for call in get.call_args_list] == [
        config["url"],
        *[f'{config["url"]}?paged={page}' for page in range(2, boundary_page + 1)],
    ]
    assert len(result.items) == len({item.id for item in result.items}) == count
    assert all("2026-10-01" <= item.published < "2026-11-01" for item in result.items)
    assert min(item.published for item in result.items) == earliest
    repeated_id = hashlib.sha256(identity.encode()).hexdigest()[:16]
    assert sum(item.id == repeated_id for item in result.items) == 1
    assert all(item.url != duplicate.findtext("link") for item in result.items)
    assert not caplog.records


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
    # The retry succeeds, but this rolling feed has no pre-window history.
    assert results[0]["status"] == "partial"
    assert results[0]["items"] == 1
    assert get.call_count == 2
    assert all(call.kwargs["timeout"] == 30 for call in get.call_args_list)
    sleep.assert_called_once_with(1)
    health = json.loads((tmp_path / "sources/2026-11/_health.json").read_text())
    assert health["summary"]["empty"] == health["summary"]["failed"] == 0
    assert health["summary"]["succeeded"] == health["summary"]["partial"] == 1


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
