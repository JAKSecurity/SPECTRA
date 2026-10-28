import json
import os

import pytest

from src.curate.curate import load_items, deduplicate, prep_items


class TestLoadItems:
    def test_loads_items_from_json_files(self, tmp_sources_with_data):
        items = load_items(tmp_sources_with_data)
        assert len(items) == 3
        titles = {item["title"] for item in items}
        assert "CISA Releases Emergency Directive on Critical Vulnerability" in titles

    def test_returns_empty_list_for_empty_dir(self, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        items = load_items(str(empty_dir))
        assert items == []

    def test_items_include_source_name(self, tmp_sources_with_data):
        items = load_items(tmp_sources_with_data)
        sources = {item["_source"] for item in items}
        assert "cisa_alerts" in sources
        assert "nist_csrc" in sources


class TestDeduplicate:
    def test_removes_same_entry_at_same_url(self):
        items = [
            {"id": "a", "url": "https://example.com/1", "title": "First"},
            {"id": "a", "url": "https://example.com/1", "title": "Updated title"},
            {"id": "c", "url": "https://example.com/2", "title": "Second"},
        ]
        result = deduplicate(items)
        assert len(result) == 2
        assert result[0]["id"] == "a"
        assert result[1]["id"] == "c"

    def test_distinct_ids_survive_even_with_matching_title_and_date(self):
        first = {"id": "a", "url": "https://example.com/shared",
                 "title": "Update", "published": "2026-10-21"}
        second = dict(first, id="b")
        assert deduplicate([first, second]) == [first, second]

    def test_same_id_at_different_urls_survives(self):
        first = {"id": "a", "url": "https://example.com/1"}
        second = dict(first, url="https://example.com/2")
        assert deduplicate([first, second]) == [first, second]

    @pytest.mark.parametrize("first_id, second_id", [
        (None, None), ("", ""), ("a", None), (None, "a"),
    ])
    def test_missing_ids_use_normalized_title_and_date(self, first_id, second_id):
        first = {"url": "https://example.com/shared", "title": "  Policy  UPDATE ",
                 "published": "2026-10-21"}
        second = dict(first, title="policy\nupdate")
        if first_id is not None:
            first["id"] = first_id
        if second_id is not None:
            second["id"] = second_id
        assert deduplicate([first, second]) == [first]

    @pytest.mark.parametrize("changes", [
        {"title": "Different update"}, {"published": "2026-10-22"},
        {"url": "https://example.com/other"},
    ])
    def test_missing_ids_preserve_distinct_entries(self, changes):
        first = {"url": "https://example.com/shared", "title": "Policy update",
                 "published": "2026-10-21"}
        second = dict(first, **changes)
        assert deduplicate([first, second]) == [first, second]

    @pytest.mark.parametrize("metadata", [{}, {"title": "Update"},
                                            {"published": "2026-10-21"}])
    def test_incomplete_identity_is_not_enough_to_drop_items(self, metadata):
        first = dict(metadata, url="https://example.com/shared")
        second = dict(first)
        assert len(deduplicate([first, second])) == 2

    def test_preserves_order(self):
        items = [
            {"id": "z", "url": "https://example.com/z"},
            {"id": "a", "url": "https://example.com/a"},
            {"id": "m", "url": "https://example.com/m"},
        ]
        result = deduplicate(items)
        assert [i["id"] for i in result] == ["z", "a", "m"]


class TestPrepItems:
    def test_writes_prepped_json(self, tmp_sources_with_data, tmp_path):
        output_path = str(tmp_path / "drafts" / "prepped.json")
        prepped = prep_items(tmp_sources_with_data, output_path)

        assert os.path.exists(output_path)
        with open(output_path) as f:
            data = json.load(f)
        assert len(data) == 3
        assert data[0]["title"] == "CISA Releases Emergency Directive on Critical Vulnerability"

    def test_prepped_items_have_clean_schema(self, tmp_sources_with_data, tmp_path):
        output_path = str(tmp_path / "drafts" / "prepped.json")
        prepped = prep_items(tmp_sources_with_data, output_path)

        for item in prepped:
            assert "id" in item
            assert "title" in item
            assert "url" in item
            assert "summary" in item
            assert "source" in item
            assert "category_hint" in item
            # _source should be cleaned up into "source"
            assert "_source" not in item

    def test_deduplicates_items(self, tmp_path):
        """Repeated entries at the same URL collapse across fetches."""
        source_dir = tmp_path / "sources"
        source_dir.mkdir()

        # Two files with overlapping items
        file1 = {
            "source": "feed_a",
            "fetched_at": "2026-04-07T09:00:00Z",
            "items": [
                {"id": "x", "title": "Shared Item", "url": "https://example.com/shared",
                 "published": "2026-04-07", "summary": "Dup.", "category_hint": "news"}
            ]
        }
        file2 = {
            "source": "feed_b",
            "fetched_at": "2026-04-07T09:00:00Z",
            "items": [
                {"id": "x", "title": "Shared Item Copy", "url": "https://example.com/shared",
                 "published": "2026-04-07", "summary": "Dup copy.", "category_hint": "news"},
                {"id": "z", "title": "Unique Item", "url": "https://example.com/unique",
                 "published": "2026-04-07", "summary": "Unique.", "category_hint": "news"}
            ]
        }

        with open(source_dir / "feed_a_20260407.json", "w") as f:
            json.dump(file1, f)
        with open(source_dir / "feed_b_20260407.json", "w") as f:
            json.dump(file2, f)

        output_path = str(tmp_path / "prepped.json")
        prepped = prep_items(str(source_dir), output_path)

        assert len(prepped) == 2
        urls = [item["url"] for item in prepped]
        assert urls.count("https://example.com/shared") == 1
