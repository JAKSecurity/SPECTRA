from unittest.mock import patch, MagicMock
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

    def test_fetch_uses_default_category_hint(self, sample_rss_xml):
        config = {"url": "https://example.com/feed.xml"}
        fetcher = RSSFetcher("test_feed", config)

        with patch("src.collect.fetchers.rss.feedparser.parse") as mock_parse:
            import feedparser
            mock_parse.return_value = feedparser.parse(sample_rss_xml)
            result = fetcher.fetch()

        assert result.items[0].category_hint == "news"

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
