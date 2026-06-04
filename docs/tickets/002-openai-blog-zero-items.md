# 002: openai_blog source regressed to 0 items in 2026-06
**Status**: Open  **Priority**: P2  **Type**: Bug
**Created**: 2026-06-03

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

## References
- Source collector: `src/` OpenAI blog fetcher (`openai_blog`)
- Design: `docs/superpowers/specs/2026-04-10-spectra-design.md` (OpenAI Blog RSS source)
- Health reports: `data/sources/<YYYY-MM>/_health.json`
- Related: AI Assistant AIA-089 (auto-escalation loop)
