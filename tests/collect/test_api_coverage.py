"""API coverage reaches saved health without changing collected item records."""
import hashlib
import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from tests.collect.test_coverage_health import collect


def reply(data):
    return Mock(status_code=200, json=Mock(return_value=data))


def item(identity, title, url, published, summary, category):
    return dict(id=hashlib.sha256(identity.encode()).hexdigest()[:16],
                title=title, url=url, published=published, summary=summary,
                category_hint=category)


def assert_saved(tmp_path, source, expected, pages, cap, boundary, status):
    results, health = collect(tmp_path, {source: {"type": source,
        **({"api_key": "synthetic-test-placeholder"} if source == "congress_gov" else {})}})
    entry = results[0]
    assert entry["status"] == status
    assert entry["pages_fetched"] == pages
    assert entry["page_cap_reached"] is cap
    assert entry["window_start_reached"] is boundary
    saved = json.loads(Path(entry["file"]).read_text())
    assert saved["items"] == expected
    assert entry["items"] == len(expected)
    for field in ("status", "pages_fetched", "page_cap_reached", "window_start_reached"):
        assert saved[field] == entry[field]
    assert health["summary"]["partial"] == (status == "partial")
    return entry


@pytest.mark.parametrize("pages, more", [(1, False), (2, False), (10, False), (10, True)])
def test_federal_register_coverage_and_unchanged_items(tmp_path, pages, more):
    doc = dict(document_number="doc-1", title="<b>Cyber policy</b>",
               html_url="https://example.test/doc", publication_date="2026-10-12",
               abstract="<p>Policy summary.</p>")
    responses = [reply(dict(results=[doc], count=pages + int(more),
        next_page_url="https://example.test/next" if i < pages - 1 or more else None))
        for i in range(pages)]
    with patch("src.collect.fetchers.federal_register.requests.get", side_effect=responses) as get:
        assert_saved(tmp_path, "federal_register", [item("doc-1", "Cyber policy",
            doc["html_url"], "2026-10-12", "Policy summary.", "policy")],
            pages, more, True, "partial" if more else "ok")
    assert get.call_count == pages
    params = get.call_args_list[0].kwargs["params"]
    assert params["conditions[publication_date][gte]"] == "2026-10-01"
    assert params["conditions[publication_date][lt]"] == "2026-11-01"


@pytest.mark.parametrize("empty", [False, True])
def test_kev_full_catalog_has_no_cap_and_unchanged_items(tmp_path, empty):
    catalog = [] if empty else [
        dict(cveID="CVE-2026-1234", dateAdded=date, vulnerabilityName="Example",
             shortDescription="Description.", dueDate="2026-10-31")
        for date in ("2026-09-30", "2026-10-12", "2026-11-01")]
    expected = [] if empty else [item("CVE-2026-1234", "CVE-2026-1234: Example",
        "https://nvd.nist.gov/vuln/detail/CVE-2026-1234", "2026-10-12",
        "Description. Remediation due by 2026-10-31.", "threats")]
    with patch("src.collect.fetchers.cisa_kev.requests.get",
               return_value=reply({"vulnerabilities": catalog})) as get:
        assert_saved(tmp_path, "cisa_kev", expected, 1, False, True, "ok")
    get.assert_called_once()


@pytest.mark.parametrize("older_date, boundary", [("2026-09-30", True),
    ("2026-10-01", None), ("", None), ("invalid", None)])
def test_congress_action_boundary_and_unchanged_items(tmp_path, older_date, boundary):
    bill = dict(congress=119, type="HR", number="3", title="Cybersecurity Act",
                latestAction=dict(actionDate="2026-10-12", text="Referred."))
    # An older action on an irrelevant bill still proves an observed boundary.
    other = dict(congress=119, type="HR", number="2", title="Unrelated",
                 latestAction=dict(actionDate=older_date))
    pages = [reply(dict(bills=[bill, other], pagination={"next": "unused"})),
             reply(dict(bills=[bill], pagination={}))]
    expected = [item("HR3-119", "HR 3 - Cybersecurity Act",
        "https://www.congress.gov/bill/119th-congress/house-bill/3", "2026-10-12",
        "HR 3: Cybersecurity Act Latest action (2026-10-12): Referred.", "legislative")]
    with patch("src.collect.fetchers.congress_gov.requests.get", side_effect=pages) as get:
        assert_saved(tmp_path, "congress_gov", expected, 2, False, boundary, "ok")
    assert get.call_count == 2
    assert get.call_args.kwargs["params"]["offset"] == 250
    assert "api_key" not in get.call_args.kwargs["params"]


def test_congress_cap_preserves_health_error_and_no_item_file(tmp_path):
    with patch("src.collect.fetchers.congress_gov.requests.get",
               return_value=reply(dict(bills=[], pagination={"next": "unused"}))) as get:
        results, health = collect(tmp_path, {"congress_gov": {
            "type": "congress_gov", "api_key": "synthetic-test-placeholder", "max_pages": 1}})
    get.assert_called_once()
    assert results[0]["status"] == "error"
    assert results[0]["error"] == "congress_gov page limit reached; report window incomplete"
    assert results[0]["pages_fetched"] is None
    assert health["summary"]["failed"] == 1
    assert health["summary"]["partial"] == 0
    assert list((tmp_path / "sources/2026-11").glob("*.json")) == [
        tmp_path / "sources/2026-11/_health.json"]


def test_congress_empty_complete_update_window_keeps_action_boundary_unknown(tmp_path):
    with patch("src.collect.fetchers.congress_gov.requests.get",
               return_value=reply(dict(bills=[], pagination={}))):
        assert_saved(tmp_path, "congress_gov", [], 1, False, None, "ok")


def test_federal_register_empty_page_is_complete(tmp_path):
    with patch("src.collect.fetchers.federal_register.requests.get",
               return_value=reply(dict(results=[], count=0, next_page_url=None))):
        assert_saved(tmp_path, "federal_register", [], 1, False, True, "ok")


def test_congress_missing_key_keeps_coverage_unknown(tmp_path, monkeypatch):
    monkeypatch.delenv("CONGRESS_GOV_API_KEY", raising=False)
    with patch("src.collect.fetchers.congress_gov._keyring_api_key", return_value=""), \
         patch("src.collect.fetchers.congress_gov.requests.get") as get:
        results, _ = collect(tmp_path, {"congress_gov": {"type": "congress_gov"}})
    get.assert_not_called()
    assert results[0]["status"] == "unavailable"
    assert results[0]["items"] is None
    assert all(results[0][field] is None for field in
               ("pages_fetched", "page_cap_reached", "window_start_reached"))
