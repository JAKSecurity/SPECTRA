import json
import os
from src.collect.fetchers.base import FetchedItem, FetchResult, BaseFetcher


class TestFetchedItem:
    def test_to_dict(self):
        item = FetchedItem(
            id="abc123",
            title="Test Title",
            url="https://example.com/test",
            published="2026-04-07",
            summary="Test summary.",
            category_hint="policy",
        )
        d = item.to_dict()
        assert d["id"] == "abc123"
        assert d["title"] == "Test Title"
        assert d["url"] == "https://example.com/test"
        assert d["published"] == "2026-04-07"
        assert d["summary"] == "Test summary."
        assert d["category_hint"] == "policy"


class TestFetchResult:
    def test_to_dict(self):
        item = FetchedItem(
            id="abc123",
            title="Test",
            url="https://example.com",
            published="2026-04-07",
            summary="Summary.",
            category_hint="news",
        )
        result = FetchResult(
            source="test_source",
            fetched_at="2026-04-07T09:00:00Z",
            items=[item],
        )
        d = result.to_dict()
        assert d["source"] == "test_source"
        assert d["fetched_at"] == "2026-04-07T09:00:00Z"
        assert len(d["items"]) == 1
        assert d["items"][0]["id"] == "abc123"

    def test_to_dict_empty_items(self):
        result = FetchResult(source="empty", fetched_at="2026-04-07T09:00:00Z", items=[])
        d = result.to_dict()
        assert d["items"] == []


class TestBaseFetcherSave:
    def test_save_creates_json_file(self, tmp_output_dir):
        item = FetchedItem(
            id="abc123",
            title="Test",
            url="https://example.com",
            published="2026-04-07",
            summary="Summary.",
            category_hint="news",
        )
        result = FetchResult(
            source="test_source",
            fetched_at="2026-04-07T09:00:00Z",
            items=[item],
        )

        class ConcreteFetcher(BaseFetcher):
            def fetch(self):
                return result

        fetcher = ConcreteFetcher("test_source", {})
        filepath = fetcher.save(result, tmp_output_dir)

        assert os.path.exists(filepath)
        assert filepath.endswith(".json")

        with open(filepath) as f:
            data = json.load(f)
        assert data["source"] == "test_source"
        assert len(data["items"]) == 1

    def test_save_creates_output_dir_if_missing(self, tmp_path):
        new_dir = str(tmp_path / "new" / "nested" / "dir")
        result = FetchResult(source="test", fetched_at="2026-04-07T09:00:00Z", items=[])

        class ConcreteFetcher(BaseFetcher):
            def fetch(self):
                return result

        fetcher = ConcreteFetcher("test", {})
        filepath = fetcher.save(result, new_dir)
        assert os.path.exists(filepath)


from src.collect.fetchers import get_fetcher
from src.collect.fetchers.rss import RSSFetcher


class TestFetcherRegistry:
    def test_get_rss_fetcher(self):
        fetcher = get_fetcher("test", {"type": "rss", "url": "https://example.com"})
        assert isinstance(fetcher, RSSFetcher)
        assert fetcher.name == "test"

    def test_get_fetcher_defaults_to_rss(self):
        fetcher = get_fetcher("test", {"url": "https://example.com"})
        assert isinstance(fetcher, RSSFetcher)

    def test_get_fetcher_unknown_type_raises(self):
        import pytest
        with pytest.raises(ValueError, match="Unknown fetcher type"):
            get_fetcher("test", {"type": "nonexistent"})
