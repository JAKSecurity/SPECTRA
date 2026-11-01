"""Offline capture, retention, preparation and cumulative-health regressions."""
import importlib.util
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest
import requests
import yaml

from src.collect.capture import run_capture
from src.collect.runner import run_collect
from src.curate.curate import prep_items


def feed_response(*days, changed=False, updated=False):
    entries = ''.join(
        f'<item><guid>story-{day}</guid><title>{"Updated" if changed or updated else "Original"}</title>'
        f'<link>https://example.test/{"new/" if changed else ""}{day}</link>'
        f'<pubDate>{datetime.fromisoformat(day).strftime("%a, %d %b %Y")} 12:00:00 GMT</pubDate>'
        '<description>Summary</description></item>' for day in days
    )
    response = requests.Response()
    response.status_code = 200
    response._content = f'<rss version="2.0"><channel><title>Test</title>{entries}</channel></rss>'.encode()
    return response


@pytest.fixture
def config(tmp_path):
    path = tmp_path / 'config.yaml'
    path.write_text(yaml.safe_dump({'sources': {
        'short': {'type': 'rss', 'url': 'https://example.test/feed', 'capture': True},
        'monthly': {'type': 'rss', 'url': 'https://example.test/monthly'},
        'disabled': {'type': 'rss', 'capture': True, 'enabled': False},
    }}))
    return str(path)


def capture(config, tmp_path, *days, changed=False, updated=False, fetched_at=None):
    with patch('src.collect.fetchers.rss.requests.get', return_value=feed_response(*days, changed=changed, updated=updated)):
        if fetched_at:
            with patch('src.collect.fetchers.rss.datetime') as clock:
                clock.side_effect = datetime
                clock.now.return_value = datetime.fromisoformat(fetched_at)
                return run_capture(config, str(tmp_path / 'sources'), today=date(2026, 11, 10))
        return run_capture(config, str(tmp_path / 'sources'), today=date(2026, 11, 10))


def test_same_day_captures_never_overwrite_even_at_identical_clock(config, tmp_path):
    with patch('src.collect.fetchers.base.datetime') as clock:
        clock.now.return_value = datetime(2026, 11, 10, 6, tzinfo=timezone.utc)
        first = capture(config, tmp_path, '2026-11-01')[0]
        before = Path(first['file']).read_bytes()
        second = capture(config, tmp_path, '2026-11-02')[0]
    assert first['file'] != second['file']
    assert Path(first['file']).read_bytes() == before
    assert len(list((tmp_path / 'sources/2026-12').glob('short_capture_*.json'))) == 2


@pytest.mark.parametrize('today,issue,start,end', [
    (date(2026, 11, 10), '2026-12', '2026-11-01', '2026-12-01'),
    (date(2026, 12, 31), '2027-01', '2026-12-01', '2027-01-01'),
])
def test_capture_routes_to_next_issue_and_only_selected_sources(config, tmp_path, today, issue, start, end):
    with patch('src.collect.fetchers.rss.requests.get', return_value=feed_response(start)) as get:
        results = run_capture(config, str(tmp_path / 'sources'), today=today)
    assert [r['source'] for r in results] == ['short']
    assert get.call_count == 1
    health = json.loads((tmp_path / 'sources' / issue / '_health.json').read_text())
    assert health['content_window'] == {'start': start, 'end_exclusive': end}
    assert Path(results[0]['file']).parent.name == issue
    assert json.loads(Path(results[0]['file']).read_text())['items'][0]['published'] == start


@pytest.mark.parametrize('changed', [False, True])
def test_captures_merge_latest_identity_despite_url_changes(config, tmp_path, changed):
    capture(config, tmp_path, '2026-11-02', '2026-11-01',
            fetched_at='2026-11-03T06:00:00+00:00')
    capture(config, tmp_path, '2026-11-02', '2026-11-04', changed=changed, updated=True,
            fetched_at='2026-11-05T06:00:00+00:00')
    # Reverse filename ordering: fetched_at, rather than filenames, owns recency.
    folder = tmp_path / 'sources/2026-12'
    files = sorted(folder.glob('short_capture_*.json'))
    files[0].rename(folder / 'zzz.json')
    prepped = prep_items(str(folder), str(tmp_path / 'prepped.json'))
    assert len(prepped) == 3
    repeated = next(i for i in prepped if i['published'] == '2026-11-02')
    assert repeated['title'] == 'Updated'
    assert repeated['url'] == f'https://example.test/{"new/" if changed else ""}2026-11-02'
    assert all(not any(k.startswith('_') for k in i) for i in prepped)


@pytest.mark.parametrize('gap', [False, True])
def test_aggregate_health_and_gap_warnings(config, tmp_path, capsys, gap):
    capture(config, tmp_path, '2026-10-31', '2026-11-01', '2026-11-03',
            fetched_at='2026-11-04T06:00:00+00:00')
    results = capture(config, tmp_path, '2026-11-07',
                      '2026-11-05' if gap else '2026-11-03',
                      fetched_at='2026-11-08T06:00:00+00:00')
    entry = results[0]
    assert entry['status'] == ('partial' if gap else 'ok')
    assert entry['window_start_reached'] is True
    folder = tmp_path / 'sources/2026-12'
    ledger = json.loads((folder / '_captures.json').read_text())
    assert ledger['short']['gaps'] == ([{'after': '2026-11-03', 'before': '2026-11-05'}] if gap else [])
    # Raw evidence must not inherit the aggregate boundary.
    assert json.loads(Path(entry['file']).read_text())['window_start_reached'] is False
    with patch('src.collect.fetchers.rss.requests.get', return_value=feed_response('2026-11-07', '2026-11-30')), patch('src.collect.fetchers.rss.datetime') as clock:
        clock.side_effect = datetime
        clock.now.return_value = datetime(2026, 12, 1, tzinfo=timezone.utc)
        monthly = next(r for r in run_collect(config, str(tmp_path / 'sources'), '2026-12') if r['source'] == 'short')
    assert monthly['status'] == entry['status']
    assert monthly['window_start_reached'] is True
    assert '_capture_' not in monthly['file']
    health = json.loads((folder / '_health.json').read_text())
    output = capsys.readouterr().out
    if gap:
        assert any('rollover gap after 2026-11-03 before 2026-11-05' in w for w in health['warnings'])
        assert 'WARNING short: rollover gap after 2026-11-03 before 2026-11-05' in output
    else:
        assert not output


@pytest.mark.parametrize('days', [(), ('2026-11-03',), ('2026-10-31', '2026-11-03')])
def test_monthly_without_captures_preserves_health_and_files(config, tmp_path, days):
    with patch('src.collect.fetchers.rss.requests.get', return_value=feed_response(*days)):
        marked = run_collect(config, str(tmp_path / 'marked'), '2026-12')
        settings = yaml.safe_load(Path(config).read_text())
        settings['sources']['short'].pop('capture')
        Path(config).write_text(yaml.safe_dump(settings))
        legacy = run_collect(config, str(tmp_path / 'legacy'), '2026-12')
    for actual, expected in zip(marked, legacy):
        assert {k: v for k, v in actual.items() if k != 'file'} == {k: v for k, v in expected.items() if k != 'file'}
        assert Path(actual['file']).name == Path(expected['file']).name
    for base in ('marked', 'legacy'):
        assert not (tmp_path / base / '2026-12/_captures.json').exists()
    first = json.loads((tmp_path / 'marked/2026-12/_health.json').read_text())
    second = json.loads((tmp_path / 'legacy/2026-12/_health.json').read_text())
    first.pop('timestamp'); second.pop('timestamp')
    for health in (first, second):
        for source in health['sources']:
            source.pop('file')
    assert first == second


def test_config_source_decision():
    sources = yaml.safe_load(Path('src/collect/config.yaml').read_text())['sources']
    assert 'the_record' not in sources
    assert 'the_verge_ai' not in sources
    assert sources['krebs_on_security'] == {
        'type': 'rss', 'url': 'https://krebsonsecurity.com/feed/',
        'category_hint': 'news', 'enabled': True,
    }
    assert len(sources) == 16
    assert {name for name, cfg in sources.items() if cfg.get('capture')} == {'cisa_alerts', 'nextgov', 'dark_reading'}


@pytest.mark.parametrize('gap', [False, True])
def test_read_only_checker_uses_capture_history(config, tmp_path, capsys, monkeypatch, gap):
    capture(config, tmp_path, '2026-10-31', '2026-11-03',
            fetched_at='2026-11-04T06:00:00+00:00')
    folder = tmp_path / 'sources/2026-12'
    before = {p.name: p.read_bytes() for p in folder.iterdir()}
    spec = importlib.util.spec_from_file_location('capture_checker', 'scripts/check-source-window.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    monkeypatch.setattr(checker, 'load_config', lambda _: {'sources': {'short': {'capture': True, 'type': 'rss', 'url': 'https://example.test/feed'}}})
    monkeypatch.setattr(sys, 'argv', ['check', '--all', '--report-month', '2026-12', '--source-dir', str(folder)])
    with patch('src.collect.fetchers.rss.requests.get', return_value=feed_response('2026-11-05' if gap else '2026-11-03', '2026-11-06')), patch('src.collect.fetchers.rss.datetime') as clock:
        clock.side_effect = datetime
        clock.now.return_value = datetime(2026, 11, 8, tzinfo=timezone.utc)
        assert checker.main() == 0
    output = capsys.readouterr().out
    assert ('partial=1' if gap else 'ok=1') in output
    if gap:
        assert 'rollover gap after 2026-11-03 before 2026-11-05' in output
    assert before == {p.name: p.read_bytes() for p in folder.iterdir()}


def test_capture_without_boundary_is_partial(config, tmp_path):
    entry = capture(config, tmp_path, '2026-11-05', '2026-11-07')[0]
    assert entry['status'] == 'partial'
    assert entry['window_start_reached'] is False
    assert entry['gaps'] == []


def test_monthly_snapshot_is_latest_version_in_preparation(config, tmp_path):
    capture(config, tmp_path, '2026-10-31', '2026-11-03',
            fetched_at='2026-11-04T06:00:00+00:00')
    with patch('src.collect.fetchers.rss.requests.get', return_value=feed_response('2026-11-03', changed=True)), patch('src.collect.fetchers.rss.datetime') as clock:
        clock.side_effect = datetime
        clock.now.return_value = datetime(2026, 12, 1, tzinfo=timezone.utc)
        run_collect(config, str(tmp_path / 'sources'), '2026-12')
    prepped = prep_items(str(tmp_path / 'sources/2026-12'), str(tmp_path / 'prepped.json'))
    assert len(prepped) == 1  # Existing cross-source URL dedup still applies.
    assert prepped[0]['title'] == 'Updated'
    assert prepped[0]['url'] == 'https://example.test/new/2026-11-03'


def test_observed_gap_is_not_erased_by_later_backfill(config, tmp_path):
    capture(config, tmp_path, '2026-10-31', '2026-11-03',
            fetched_at='2026-11-04T06:00:00+00:00')
    capture(config, tmp_path, '2026-11-05', '2026-11-07',
            fetched_at='2026-11-08T06:00:00+00:00')
    # Simulate a corrected old snapshot: the recorded gap is still evidence.
    folder = tmp_path / 'sources/2026-12'
    for path in folder.glob('short_capture_*.json'):
        snapshot = json.loads(path.read_text())
        if snapshot['fetched_at'].startswith('2026-11-08'):
            snapshot['items'][0]['published'] = '2026-11-03'
            path.write_text(json.dumps(snapshot))
    entry = capture(config, tmp_path, '2026-11-07', '2026-11-09',
                    fetched_at='2026-11-10T06:00:00+00:00')[0]
    assert entry['status'] == 'partial'
    assert entry['gaps'] == [{'after': '2026-11-03', 'before': '2026-11-05'}]


def test_interrupted_capture_does_not_publish_invalid_json(tmp_path):
    from src.collect.fetchers.base import FetchResult
    from src.collect.fetchers.rss import RSSFetcher

    fetcher = RSSFetcher('short', {})
    with patch('src.collect.fetchers.base.json.dump', side_effect=OSError('synthetic write interruption')):
        with pytest.raises(OSError, match='synthetic write interruption'):
            fetcher.save(FetchResult('short', '2026-11-10T06:00:00Z', []), str(tmp_path), capture=True)
    assert not list(tmp_path.glob('*.json'))
    assert list(tmp_path.glob('*.tmp'))


def test_monthly_without_captures_ignores_unrelated_broken_snapshot(config, tmp_path):
    folder = tmp_path / 'sources/2026-12'
    folder.mkdir(parents=True)
    broken = folder / 'other_20261130.json'
    broken.write_text('{')
    with patch('src.collect.fetchers.rss.requests.get',
               return_value=feed_response('2026-10-31', '2026-11-03')):
        results = run_collect(config, str(tmp_path / 'sources'), '2026-12')
    short = next(result for result in results if result['source'] == 'short')
    assert short['status'] == 'ok'
    assert short['window_start_reached'] is True
    assert not (folder / '_captures.json').exists()
    assert broken.read_text() == '{'
