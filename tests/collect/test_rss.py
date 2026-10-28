import hashlib
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.curate.curate import prep_items
from src.collect.fetchers.rss import RSSFetcher, _strip_html


class TestRSSFetcher:
    def test_fetch_parses_rss_items(self, sample_rss_xml):
        config = {"url": "https://example.com/feed.xml", "category_hint": "policy"}
        fetcher = RSSFetcher("test_feed", config)

        with patch("src.collect.fetchers.rss.feedparser.parse") as mock_parse:
            import feedparser
            mock_parse.return_value = feedparser.parse(sample_rss_xml)
            result = fetcher.fetch()

        assert result.source == "test_feed"
        assert len(result.items) == 3
        assert result.items[0].title == "CISA Releases Emergency Directive on Critical Vulnerability"
        assert result.items[0].url == "https://example.com/cisa-ed-2026-01"
        assert result.items[0].category_hint == "policy"
        assert result.items[0].published == "2026-04-06"

    def test_fetch_generates_stable_ids(self, sample_rss_xml):
        config = {"url": "https://example.com/feed.xml", "category_hint": "news"}
        fetcher = RSSFetcher("test_feed", config)

        with patch("src.collect.fetchers.rss.feedparser.parse") as mock_parse:
            import feedparser
            parsed = feedparser.parse(sample_rss_xml)
            mock_parse.return_value = parsed
            result1 = fetcher.fetch()
            mock_parse.return_value = feedparser.parse(sample_rss_xml)
            result2 = fetcher.fetch()

        assert result1.items[0].id == result2.items[0].id
        assert result1.items[0].id != result1.items[1].id

    def test_fedramp_shared_link_survives_collection_and_prep(self, tmp_path):
        fixture = Path(__file__).parent / "fixtures" / "fedramp-changelog.xml"
        fetcher = RSSFetcher("fedramp_changelog", {
            "url": "https://www.fedramp.gov/changelog/rss.xml",
            "start_date": "2026-10-01",
            "end_date": "2026-11-01",
        })
        response = MagicMock()
        response.content = fixture.read_bytes()
        with patch("src.collect.fetchers.rss.requests.get", return_value=response):
            result = fetcher.fetch()
            repeated = fetcher.fetch()

        assert len(result.items) == 4
        assert len({item.id for item in result.items}) == 4
        assert [item.id for item in result.items] == [
            hashlib.sha256(f"https://www.fedramp.gov/changelog/{n}".encode()).hexdigest()[:16]
            for n in (98, 97, 96, 95)
        ]
        assert {item.url for item in result.items} == {"https://www.fedramp.gov/changelog"}
        assert [item.published for item in result.items] == [
            "2026-10-21", "2026-10-15", "2026-10-14", "2026-10-08",
        ]
        source_dir = tmp_path / "sources"
        source_dir.mkdir()
        for name, fetched in (("first", result), ("repeat", repeated)):
            (source_dir / f"{name}.json").write_text(json.dumps(fetched.to_dict()))
        output_path = tmp_path / "drafts" / "prepped.json"
        prepped = prep_items(str(source_dir), str(output_path))
        assert [item["id"] for item in prepped] == [item.id for item in result.items]
        assert [item["title"] for item in prepped] == [item.title for item in result.items]
        assert json.loads(output_path.read_text()) == prepped

    @pytest.mark.parametrize("guid", ["", "<guid isPermaLink='false'></guid>",
                                      "<guid isPermaLink='false'>   </guid>"])
    def test_missing_feed_id_hashes_link(self, guid):
        xml = f"""<rss version="2.0"><channel><item>
            <title>No identifier</title><link>https://example.com/article</link>
            {guid}</item></channel></rss>"""
        response = MagicMock()
        response.content = xml.encode()
        with patch("src.collect.fetchers.rss.requests.get", return_value=response):
            result = RSSFetcher("test", {"url": "https://example.com/feed"}).fetch()
        assert result.items[0].id == hashlib.sha256(
            b"https://example.com/article").hexdigest()[:16]
        assert result.items[0].url == "https://example.com/article"

    def test_feed_id_is_not_used_as_reader_url(self):
        response = MagicMock()
        response.content = b"""<rss version="2.0"><channel><item>
            <title>No reader link</title><guid isPermaLink="false">entry-98</guid>
            </item></channel></rss>"""
        with patch("src.collect.fetchers.rss.requests.get", return_value=response):
            result = RSSFetcher("test", {"url": "https://example.com/feed"}).fetch()
        assert result.items[0].url == ""
        assert result.items[0].id == hashlib.sha256(b"entry-98").hexdigest()[:16]

    def test_fetch_uses_default_category_hint(self, sample_rss_xml):
        config = {"url": "https://example.com/feed.xml"}
        fetcher = RSSFetcher("test_feed", config)

        with patch("src.collect.fetchers.rss.feedparser.parse") as mock_parse:
            import feedparser
            mock_parse.return_value = feedparser.parse(sample_rss_xml)
            result = fetcher.fetch()

        assert result.items[0].category_hint == "news"

    def test_filters_to_explicit_content_window(self, sample_rss_xml):
        config = {
            "url": "https://example.com/feed.xml",
            "start_date": "2026-04-05",
            "end_date": "2026-04-07",
        }
        fetcher = RSSFetcher("test_feed", config)

        with patch("src.collect.fetchers.rss.feedparser.parse") as mock_parse:
            import feedparser
            mock_parse.return_value = feedparser.parse(sample_rss_xml)
            result = fetcher.fetch()

        assert [item.published for item in result.items] == ["2026-04-06"]

    def test_fetch_handles_empty_feed(self):
        empty_rss = '<?xml version="1.0"?><rss version="2.0"><channel></channel></rss>'
        config = {"url": "https://example.com/empty.xml", "category_hint": "policy"}
        fetcher = RSSFetcher("empty_feed", config)

        with patch("src.collect.fetchers.rss.feedparser.parse") as mock_parse:
            import feedparser
            mock_parse.return_value = feedparser.parse(empty_rss)
            result = fetcher.fetch()

        assert result.source == "empty_feed"
        assert len(result.items) == 0


class TestStripHtml:
    def test_removes_tags(self):
        assert _strip_html("<p>Hello <b>world</b></p>") == "Hello world"

    def test_decodes_entities(self):
        assert _strip_html("AT&amp;T &lt;security&gt;") == "AT&T <security>"

    def test_collapses_whitespace(self):
        assert _strip_html("<p>Line one</p>  <p>Line two</p>") == "Line one Line two"

    def test_handles_plain_text(self):
        assert _strip_html("No HTML here") == "No HTML here"
