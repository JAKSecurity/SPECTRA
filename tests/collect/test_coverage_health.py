"""Offline coverage metadata and production health-report regressions."""
import json
import re
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests
import yaml

from src.collect.fetchers.base import BaseFetcher, FetchResult, FetchedItem
from src.collect.fetchers.rss import RSSFetcher
from src.collect.runner import main, run_collect


FIXTURES = Path(__file__).parent / "fixtures"


def response(filename):
    result = requests.Response()
    result.status_code = 200
    result._content = (FIXTURES / filename).read_bytes()
    return result


def collect(tmp_path, sources):
    config = tmp_path / "config.yaml"
    config.write_text(yaml.safe_dump({"sources": sources}))
    results = run_collect(str(config), str(tmp_path / "sources"), "2026-11")
    health = json.loads((tmp_path / "sources/2026-11/_health.json").read_text())
    assert health["sources"] == results
    return results, health


@pytest.mark.parametrize("crosses_start", [False, True])
def test_rss_cap_and_boundary_reach_runner_health(tmp_path, crosses_start):
    pages = [response("wordpress-page-1.xml")]
    if crosses_start:
        pages += [response("wordpress-page-2.xml"), response("wordpress-page-3.xml")]
    source = {"type": "rss", "url": "https://example.test/feed",
              "paged": True, "max_pages": len(pages)}
    with patch("src.collect.fetchers.rss.requests.get", side_effect=pages) as get:
        results, health = collect(tmp_path, {"feed": source})
    entry = results[0]
    assert entry["status"] == ("ok" if crosses_start else "partial")
    assert entry["pages_fetched"] == get.call_count == len(pages)
    assert entry["page_cap_reached"] is (not crosses_start)
    assert entry["window_start_reached"] is crosses_start
    assert entry["items"] == (3 if crosses_start else 2)
    saved = json.loads(Path(entry["file"]).read_text())
    assert saved["status"] == entry["status"]
    assert len(saved["items"]) == entry["items"]
    for field in ("pages_fetched", "page_cap_reached", "window_start_reached"):
        assert saved[field] == entry[field]
    assert health["summary"]["succeeded"] == 1
    assert health["summary"]["total_items"] == entry["items"]
    assert health["summary"]["partial"] == (0 if crosses_start else 1)
    if not crosses_start:
        assert any("partial" in warning for warning in health["warnings"])


@pytest.mark.parametrize("fixture, start, expected", [
    ("wordpress-page-1.xml", "2026-10-01", False),
    ("wordpress-page-1.xml", "2026-10-27", False),  # Equality is not past the start.
    ("wordpress-page-2.xml", "2026-10-01", True),
    ("empty-feed.xml", "2026-10-01", None),
    ("wordpress-page-1.xml", None, None),
])
def test_unpaged_rss_coverage(fixture, start, expected):
    config = {"url": "https://example.test/feed", "start_date": start}
    with patch("src.collect.fetchers.rss.requests.get", return_value=response(fixture)):
        result = RSSFetcher("feed", config).fetch()
    assert result.pages_fetched == 1
    assert result.page_cap_reached is False
    assert result.window_start_reached is expected


@pytest.mark.parametrize("paged", [False, True])
def test_undated_rss_boundary_is_unknown(tmp_path, paged):
    feed = response("wordpress-page-3.xml")
    feed._content = re.sub(rb"<pubDate>.*?</pubDate>", b"", feed.content)
    with patch("src.collect.fetchers.rss.requests.get", return_value=feed):
        results, health = collect(tmp_path, {"feed": {
            "type": "rss", "url": "https://example.test/feed", "paged": paged,
        }})
    assert results[0]["window_start_reached"] is None
    assert results[0]["page_cap_reached"] is paged
    assert results[0]["status"] == ("partial" if paged else "ok")
    assert health["summary"]["empty"] == 1


def test_unpaged_short_history_is_partial_without_cap(tmp_path):
    with patch("src.collect.fetchers.rss.requests.get", return_value=response("wordpress-page-1.xml")):
        results, health = collect(tmp_path, {"feed": {"type": "rss", "url": "https://example.test/feed"}})
    assert results[0]["status"] == "partial"
    assert results[0]["page_cap_reached"] is False
    assert results[0]["window_start_reached"] is False
    assert health["summary"]["partial"] == 1


def test_missing_congress_key_is_unavailable_end_to_end(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("CONGRESS_GOV_API_KEY", raising=False)
    config = tmp_path / "config.yaml"
    config.write_text(yaml.safe_dump({"sources": {"congress_gov": {
        "type": "congress_gov", "core": True,
    }}}))
    monkeypatch.setattr("sys.argv", ["collect", str(config), str(tmp_path / "sources"),
                                    "--report-month", "2026-11"])
    with patch("src.collect.fetchers.congress_gov._keyring_api_key", return_value=""), \
         patch("src.collect.fetchers.congress_gov.requests.get") as get, \
         patch("src.collect.runner.time.sleep") as sleep:
        main()
    get.assert_not_called()
    sleep.assert_not_called()
    health = json.loads((tmp_path / "sources/2026-11/_health.json").read_text())
    entry = health["sources"][0]
    assert entry["status"] == "unavailable"
    assert entry["items"] is None
    assert health["summary"] == {
        "total_sources": 1, "succeeded": 0, "failed": 0,
        "empty": 0, "total_items": 0, "partial": 0, "unavailable": 1,
    }
    assert any("unavailable" in warning for warning in health["warnings"])
    saved = json.loads(Path(entry["file"]).read_text())
    assert saved["status"] == "unavailable"
    assert saved["items"] == []  # Preserve the item-list schema for preparation.
    output = capsys.readouterr().out
    assert "unavailable" in output.lower()
    assert "unknown" in output.lower()


def test_existing_fetcher_without_coverage_keeps_ok(tmp_path):
    class ExistingFetcher(BaseFetcher):
        def fetch(self):
            return FetchResult(self.name, "2026-10-28T12:00:00Z", [
                FetchedItem("id", "Title", "https://example.test/article",
                            "2026-10-28", "Summary", "news"),
            ])

    with patch("src.collect.runner.get_fetcher", return_value=ExistingFetcher("legacy", {})):
        results, health = collect(tmp_path, {"legacy": {}})
    assert results[0]["status"] == "ok"
    assert results[0]["items"] == 1
    assert results[0]["pages_fetched"] is None
    assert results[0]["page_cap_reached"] is None
    assert results[0]["window_start_reached"] is None
    assert health["summary"]["succeeded"] == health["summary"]["total_items"] == 1


@pytest.mark.parametrize("failure", ["request", "json"])
def test_congress_errors_do_not_persist_request_details(tmp_path, failure):
    marker = "synthetic-sensitive-request-details"
    reply = response("congress-page-1.json")
    if failure == "json":
        reply = Mock(status_code=200)
        reply.json.side_effect = ValueError(marker)
    effect = requests.ConnectionError(marker) if failure == "request" else None
    with patch("src.collect.fetchers.congress_gov.requests.get", return_value=reply,
               side_effect=effect):
        results, health = collect(tmp_path, {"congress_gov": {
            "type": "congress_gov", "api_key": "synthetic-test-placeholder",
        }})
    assert results[0]["status"] == "error"
    assert marker not in json.dumps(health)
    assert "https://" not in json.dumps(health)
