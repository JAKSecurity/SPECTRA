import json
import os
from unittest.mock import patch, MagicMock

import pytest
import requests
import yaml

from src.collect.runner import load_config, main, report_window, run_collect


def test_report_window_uses_previous_calendar_month():
    assert report_window("2026-09") == ("2026-08-01", "2026-09-01")
    assert report_window("2026-01") == ("2025-12-01", "2026-01-01")


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

    def test_report_month_controls_directory_window_and_health(self, tmp_path, sample_rss_xml):
        config_path = tmp_path / "config.yaml"
        config_data = {
            "sources": {
                "feed_a": {
                    "type": "rss",
                    "url": "https://example.com/a",
                    "enabled": True,
                }
            }
        }
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        output_dir = str(tmp_path / "output")
        with patch("src.collect.fetchers.rss.feedparser.parse") as mock_parse:
            import feedparser
            mock_parse.return_value = feedparser.parse(sample_rss_xml)
            run_collect(str(config_path), output_dir, report_month="2026-05")

        month_dir = tmp_path / "output" / "2026-05"
        assert month_dir.is_dir()
        health = json.loads((month_dir / "_health.json").read_text())
        assert health["report_month"] == "2026-05"
        assert health["content_window"] == {
            "start": "2026-04-01",
            "end_exclusive": "2026-05-01",
        }

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


@pytest.mark.parametrize("api_key", [" FAKE-KEY-123", "FAKE-KEY-123\nTAIL"])
def test_malformed_congress_key_stays_out_of_results_health_and_console(
    tmp_path, monkeypatch, capsys, caplog, api_key,
):
    config = tmp_path / "config.yaml"
    config.write_text(yaml.safe_dump({"sources": {"congress_gov": {
        "type": "congress_gov", "api_key": api_key,
    }}}))
    output = tmp_path / "output"
    monkeypatch.setattr("sys.argv", ["collect", str(config), str(output),
                                     "--report-month", "2026-11"])

    # Exercise requests' actual header validation without sending a request.
    def prepare_only(url, **kwargs):
        requests.Request("GET", url, headers=kwargs["headers"]).prepare()
        raise AssertionError("Malformed header was accepted")

    results = []

    def capture_collect(*args, **kwargs):
        results.extend(run_collect(*args, **kwargs))
        return results

    with patch("src.collect.fetchers.congress_gov.requests.get", side_effect=prepare_only), patch(
        "src.collect.runner.run_collect", side_effect=capture_collect
    ):
        main()
    assert results[0]["error"] == "Congress.gov API key is malformed"
    health_text = (output / "2026-11/_health.json").read_text()
    health = json.loads(health_text)
    assert health["sources"][0]["status"] == "error"
    assert health["sources"][0]["error"] == "Congress.gov API key is malformed"
    assert health["warnings"] == ["congress_gov: Congress.gov API key is malformed"]
    captured = capsys.readouterr()
    for text in (json.dumps(results), health_text, captured.out, captured.err, caplog.text):
        assert "FAKE-KEY-123" not in text
        assert api_key not in text
    assert "ERR congress_gov: Congress.gov API key is malformed" in captured.out


def test_runner_redacts_all_configured_keys_and_preserves_diagnostics(tmp_path, capsys, caplog):
    config = tmp_path / "config.yaml"
    config.write_text(yaml.safe_dump({"sources": {
        "broken": {"type": "rss", "api_key": "FAKE-KEY-123"},
        "disabled": {"enabled": False, "api_key": "FAKE-KEY-123-LONG"},
    }}))
    message = "Failure: FAKE-KEY-123-LONG; FAKE-KEY-123; again FAKE-KEY-123 (retry)"
    expected = "Failure: [REDACTED]; [REDACTED]; again [REDACTED] (retry)"
    with patch("src.collect.runner.get_fetcher", side_effect=RuntimeError(message)):
        results = run_collect(str(config), str(tmp_path / "output"), "2026-11")
    assert results[0]["error"] == expected
    health_text = (tmp_path / "output/2026-11/_health.json").read_text()
    health = json.loads(health_text)
    assert health["sources"] == results
    assert health["warnings"] == [f"broken: {expected}"]
    captured = capsys.readouterr()
    for text in (json.dumps(results), health_text, captured.out, captured.err, caplog.text):
        assert "FAKE-KEY-123" not in text


@pytest.mark.parametrize("field", [
    "api_key", "X-Api-Key", "token", "api_token", "access_token",
    "password", "secret", "client_secret", "Authorization",
])
def test_runner_redacts_nested_credentials_literally(tmp_path, field):
    config = tmp_path / "config.yaml"
    config.write_text(yaml.safe_dump({"sources": {"broken": {
        "type": "rss", "headers": {field: "FAKE-KEY-[123].*"},
        "api_key": "", "password": None,
    }}}))
    with patch("src.collect.runner.get_fetcher", side_effect=RuntimeError(
        "Failed with FAKE-KEY-[123].*; context preserved"
    )):
        results = run_collect(str(config), str(tmp_path / "output"), "2026-11")
    assert results[0]["error"] == "Failed with [REDACTED]; context preserved"


def test_runner_redacts_environment_key(tmp_path, monkeypatch):
    config = tmp_path / "config.yaml"
    config.write_text(yaml.safe_dump({"sources": {"broken": {"type": "rss"}}}))
    monkeypatch.setenv("CONGRESS_GOV_API_KEY", "FAKE-KEY-123")
    with patch("src.collect.runner.get_fetcher", side_effect=RuntimeError(
        "Failed with FAKE-KEY-123; context preserved"
    )):
        results = run_collect(str(config), str(tmp_path / "output"), "2026-11")
    assert results[0]["error"] == "Failed with [REDACTED]; context preserved"
