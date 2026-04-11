import json
import os
from unittest.mock import patch, MagicMock

import yaml

from src.collect.runner import load_config, run_collect


class TestLoadConfig:
    def test_loads_yaml_sources(self, tmp_path):
        config_data = {
            "sources": {
                "test_feed": {
                    "type": "rss",
                    "url": "https://example.com/feed",
                    "category_hint": "news",
                    "enabled": True,
                }
            }
        }
        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        config = load_config(str(config_path))
        assert "test_feed" in config["sources"]
        assert config["sources"]["test_feed"]["url"] == "https://example.com/feed"


class TestRunCollect:
    def test_runs_enabled_fetchers_and_writes_json(self, tmp_path, sample_rss_xml):
        config_path = tmp_path / "config.yaml"
        config_data = {
            "sources": {
                "feed_a": {
                    "type": "rss",
                    "url": "https://example.com/a",
                    "category_hint": "policy",
                    "enabled": True,
                },
                "feed_b": {
                    "type": "rss",
                    "url": "https://example.com/b",
                    "category_hint": "news",
                    "enabled": True,
                },
            }
        }
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        output_dir = str(tmp_path / "output")

        with patch("src.collect.fetchers.rss.feedparser.parse") as mock_parse:
            import feedparser
            mock_parse.return_value = feedparser.parse(sample_rss_xml)
            results = run_collect(str(config_path), output_dir)

        ok_results = [r for r in results if r["status"] == "ok"]
        assert len(ok_results) == 2

        # Check JSON files were created
        month_dir = os.listdir(output_dir)
        assert len(month_dir) == 1  # one YYYY-MM dir
        json_files = os.listdir(os.path.join(output_dir, month_dir[0]))
        # 2 source JSON files + _health.json
        assert len(json_files) == 3
        assert "_health.json" in json_files

    def test_skips_disabled_fetchers(self, tmp_path, sample_rss_xml):
        config_path = tmp_path / "config.yaml"
        config_data = {
            "sources": {
                "enabled_feed": {
                    "type": "rss",
                    "url": "https://example.com/a",
                    "enabled": True,
                },
                "disabled_feed": {
                    "type": "rss",
                    "url": "https://example.com/b",
                    "enabled": False,
                },
            }
        }
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        output_dir = str(tmp_path / "output")

        with patch("src.collect.fetchers.rss.feedparser.parse") as mock_parse:
            import feedparser
            mock_parse.return_value = feedparser.parse(sample_rss_xml)
            results = run_collect(str(config_path), output_dir)

        assert len(results) == 1
        assert results[0]["source"] == "enabled_feed"

    def test_handles_fetcher_failure_gracefully(self, tmp_path):
        config_path = tmp_path / "config.yaml"
        config_data = {
            "sources": {
                "bad_feed": {
                    "type": "rss",
                    "url": "https://example.com/bad",
                    "enabled": True,
                },
            }
        }
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        output_dir = str(tmp_path / "output")

        with patch("src.collect.fetchers.rss.feedparser.parse") as mock_parse:
            mock_parse.side_effect = Exception("Network error")
            results = run_collect(str(config_path), output_dir)

        assert len(results) == 1
        assert results[0]["status"] == "error"
        assert "Network error" in results[0]["error"]
