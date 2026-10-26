# 003: cisa_alerts source returned 0 items in 2026-07 (regression)
**Status**: Delivered  **Priority**: P2  **Type**: Bug
**Created**: 2026-07-01

## Summary
The `cisa_alerts` source (CISA Cybersecurity Advisories RSS fetcher) returned a healthy
**30 items per month for three consecutive runs (2026-04, 2026-05, 2026-06)** and then
**dropped to 0 in the 2026-07 run** — a regression, analogous to the earlier `openai_blog`
feed regression (ticket 002). The source-health monitor correctly flagged it
("cisa_alerts: returned 0 items (feed may be stale or broken)").

## Context
SPECTRA is `status: archived` (project complete) but the monthly pipeline runs unattended, so
this is a live maintenance bug. CISA Alerts is a core government/policy source; losing it drops
CISA advisories from the digest. **KEV coverage is unaffected** (the separate `cisa_kev`
source returned 23 items this run), so actively-exploited-CVE coverage stayed intact — but
narrative advisories (campaigns, ICS advisories, guidance) were lost for July.

Evidence (`data/sources/<YYYY-MM>/_health.json`):
- 2026-04: cisa_alerts = 30 items
- 2026-05: cisa_alerts = 30 items
- 2026-06: cisa_alerts = 30 items
- 2026-07: cisa_alerts = 0 items

Configured feed (`src/collect/config.yaml`):
`https://www.cisa.gov/cybersecurity-advisories/all.xml` (type `rss`, category_hint `policy`).

Because it worked for three months and broke in July, the likely cause is a **feed change** —
the CISA advisories feed URL moved, changed format, added a redirect the fetcher doesn't
follow, or was temporarily unavailable at fetch time (5AM 1st-of-month). Ticket 002 was an
almost identical pattern (OpenAI feed 307-redirect not followed); check for the same class of
issue here first.

## Acceptance Criteria
- [x] Root-cause the July regression: run the `cisa_alerts` fetcher in isolation; confirm the
      feed URL resolves, returns entries, and is not redirecting to a new location the fetcher
      fails to follow.
- [x] Update the feed URL / parser (or add redirect-following) as needed.
- [x] Confirm a subsequent (or forced) run reports cisa_alerts with items > 0 in `_health.json`.
- [x] If the feed was merely transiently down, document that and consider a retry/backoff so a
      single 5AM fetch failure doesn't silently zero out a core source for the whole month.

## References
- Source collector: generic RSS fetcher (`src/collect/fetchers/rss.py`), source `cisa_alerts`
- Config: `src/collect/config.yaml` (cisa_alerts feed URL)
- Design: `docs/superpowers/specs/2026-04-10-spectra-design.md` (CISA Alerts & Advisories source)
- Health reports: `data/sources/<YYYY-MM>/_health.json`
- Related: ticket 002 (openai_blog feed regression — same class of failure); AI Assistant
  AIA-089 (auto-escalation loop)

## Resolution

Investigated 2026-10-26 for packet spectra1. The supplied native source directory
retains only August, September and October health files; July's `_health.json`
and response body are absent. The ticket records July's zero count, but there
is no retained HTTP status, content type or redirect evidence to establish an
exact cause. Treat this as a likely transient failed/empty response, not a
confirmed URL migration. Retained health counts are August 0 (a September 6
backfill), September 10 and October 30.

Live check: the configured URL returns HTTP 200 without redirects,
`application/rss+xml; charset=utf-8`, RSS 2.0, 30 entries, all inside
2026-10-01 inclusive through 2026-11-01 exclusive as of October 26. No URL
change is needed. The previous feedparser transport already followed redirects,
but empty entries were silently returned without status evidence or a retry.

The RSS transport now follows redirects using requests, checks HTTP status and
uses a 30-second timeout. The collector retries a configured core source once
after one second on either an exception or an empty report-window result,
before saving output/health. Only `cisa_alerts` is newly marked core. A second
failure remains an error; a second empty result remains an empty warning.
Offline replay covers empty XML, HTML, HTTP 503 and timeout recovery, as well
as exhausted retries. The empty-response regression test fails on the old
collector. No ticket status or acceptance checkboxes changed in this packet.
