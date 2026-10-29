"""Offline checks for the read-only source health command."""
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


@pytest.fixture
def checker(monkeypatch):
    path = Path(__file__).resolve().parents[2] / "scripts/check-source-window.py"
    spec = importlib.util.spec_from_file_location("check_source_window", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.delenv("CONGRESS_GOV_API_KEY", raising=False)
    monkeypatch.setattr(module, "_keyring_api_key", lambda: "")
    monkeypatch.setattr(sys, "argv", [str(path), "--report-month", "2026-11"])
    return module


def result(*dates):
    return SimpleNamespace(items=[SimpleNamespace(published=value) for value in dates])


def test_all_enabled_sources_in_config_order(checker, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", sys.argv + ["--all"])
    sources = checker.load_config("src/collect/config.yaml")["sources"]
    sources["disabled"] = {"enabled": False}
    sources["implicit_enabled"] = {"type": "rss"}
    monkeypatch.setattr(checker, "load_config", lambda _: {"sources": sources})
    monkeypatch.setattr(checker, "_keyring_api_key", lambda: "synthetic-test-placeholder")
    fetcher = Mock()
    fetcher.fetch.return_value = result("2026-10-20", "2026-10-02", "2026-10-10")
    factory = Mock(return_value=fetcher)
    monkeypatch.setattr(checker, "get_fetcher", factory)

    assert checker.main() == 0
    names = [name for name, config in sources.items() if config.get("enabled", True)]
    assert [call.args[0] for call in factory.call_args_list] == names
    for call in factory.call_args_list:
        assert call.args[1]["start_date"] == "2026-10-01"
        assert call.args[1]["end_date"] == "2026-11-01"
    lines = capsys.readouterr().out.splitlines()
    assert [line.split(":")[0] for line in lines[1:-1]] == names
    assert all("3 items; earliest=2026-10-02; latest=2026-10-20; ok" in line for line in lines[1:-1])
    assert f"{len(names)} sources; {3 * len(names)} items; ok={len(names)}" in lines[-1]
    fetcher.save.assert_not_called()


def test_four_statuses_and_safe_error_output(checker, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", sys.argv + ["--all"])
    sources = {"good": {}, "empty": {}, "broken": {}, "congress_gov": {"type": "congress_gov"}}
    monkeypatch.setattr(checker, "load_config", lambda _: {"sources": sources})
    marker = "synthetic-sensitive-error-marker"
    factory = Mock(side_effect=[
        SimpleNamespace(fetch=lambda: result("2026-10-03")),
        SimpleNamespace(fetch=lambda: result()),
        SimpleNamespace(fetch=Mock(side_effect=RuntimeError(f"request failed with key {marker}"))),
    ])
    monkeypatch.setattr(checker, "get_fetcher", factory)

    assert checker.main() == 1
    captured = capsys.readouterr()
    assert marker not in captured.out + captured.err
    assert captured.err == ""
    assert "good: 1 items; earliest=2026-10-03; latest=2026-10-03; ok" in captured.out
    assert "empty: 0 items; earliest=-; latest=-; zero" in captured.out
    assert "broken: unknown items; earliest=-; latest=-; failed (RuntimeError)" in captured.out
    assert "congress_gov: unknown items; earliest=-; latest=-; unavailable (no readable key; not a verified zero)" in captured.out
    assert "Summary: 4 sources; 1 items; ok=1; zero=1; failed=1; unavailable=1" in captured.out
    assert factory.call_count == 3


def test_default_checks_only_original_two_sources_and_zero_succeeds(checker, monkeypatch, capsys):
    monkeypatch.setattr(checker, "_keyring_api_key", lambda: "synthetic-test-placeholder")
    fetcher = Mock()
    fetcher.fetch.return_value = result()
    factory = Mock(return_value=fetcher)
    monkeypatch.setattr(checker, "get_fetcher", factory)

    assert checker.main() == 0
    assert [call.args[0] for call in factory.call_args_list] == ["cisa_alerts", "congress_gov"]
    assert "Summary: 2 sources; 0 items; ok=0; zero=2; failed=0; unavailable=0" in capsys.readouterr().out
    fetcher.save.assert_not_called()
