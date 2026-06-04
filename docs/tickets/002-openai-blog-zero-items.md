# 002: openai_blog source regressed to 0 items in 2026-06
**Status**: Delivered  **Priority**: P2  **Type**: Bug
**Created**: 2026-06-03  **Resolved**: 2026-06-03

## Summary
The `openai_blog` source (OpenAI Blog RSS fetcher) returned a healthy item count for two
months and then **dropped to 0 in the 2026-06 run** — a regression, distinct from the chronic
`congress_gov` failure (ticket 001). The source-health monitor flagged it ("openai_blog:
returned 0 items (feed may be stale or broken)").

## Context
SPECTRA is `status: archived` (project complete) but the monthly pipeline runs unattended, so
this is a live maintenance bug.

Evidence (`data/sources/<YYYY-MM>/_health.json`):
- 2026-04: openai_blog = 934 items
- 2026-05: openai_blog = 929 items
- 2026-06: openai_blog = 0 items

Because it worked before and broke in June, the likely cause is an **RSS feed change** — the
OpenAI blog feed URL moved or its format changed, or the feed was retired. (Note: the prior
~930-item counts are themselves unusually high for a blog feed and may indicate the collector
was pulling an over-broad endpoint; worth confirming the source is reading the intended feed
while fixing it.)

## Acceptance Criteria
- [ ] Root-cause the June regression (run the collector in isolation; check the feed URL
      resolves and returns entries; inspect the raw response).
- [ ] Update the feed URL / parser as needed.
- [ ] Confirm a subsequent (or forced) run reports openai_blog with items > 0 in `_health.json`.
- [ ] Sanity-check the item count is reasonable for a blog feed (not the prior ~930).

## Resolution (2026-06-03)
Root cause: the configured feed URL `https://openai.com/blog/rss.xml` now **307-redirects**
to `https://openai.com/news/rss.xml`. A run that did not follow the redirect returned 0 items.
The feed itself is healthy (both URLs return ~989 entries today), so June's 0 was the
redirect/transient failure, not a retired feed.

Fix: pointed `openai_blog` at the canonical non-redirecting URL
`https://openai.com/news/rss.xml` in `src/collect/config.yaml`.

Verified: ran `RSSFetcher('openai_blog', cfg).fetch()` through SPECTRA's own code path ->
**989 items** (was 0). Full suite green (59 passed). The high count is the full archive (same
as the historical 934/929); downstream curation caps to top-20 per section by relevance, so no
output flooding.

## References
- Source collector: `src/` OpenAI blog fetcher (`openai_blog`)
- Design: `docs/superpowers/specs/2026-04-10-spectra-design.md` (OpenAI Blog RSS source)
- Health reports: `data/sources/<YYYY-MM>/_health.json`
- Related: AI Assistant AIA-089 (auto-escalation loop)
