# 004: congress_gov returns bills but keyword/date filters not applied (relevance bug)
**Status**: Open  **Priority**: P2  **Type**: Bug
**Created**: 2026-07-01

## Summary
Ticket 001 fixed `congress_gov` returning **0 items** (API key wiring) — it now returns 20
bills per run. But the returned bills are **not cybersecurity-related and not within the
configured date window**: the 2026-07 run returned items like "No Aid for Ghost Students Act",
"Eliminating Fraud and Improper Payments in TANF Act", "PBM Act", wildfire-preparedness-week
and university-volleyball resolutions — with `latest action` dates ranging back to
**March 2025**. The config asks for `search_term: cybersecurity` and `days_back: 30`, so
neither the keyword filter nor the recency window is being honored. This is a distinct
**quality/relevance** bug, separate from 001's item-count bug.

## Context
Because the bills are irrelevant, the Legislative Highlights section gets no usable material
from this source. For the 2026-07 digest the section was salvaged from **news-sourced**
legislative movement (NDAA amendment codifying CISA's vuln-tracking role; Warner bills on cyber
info-sharing and critical-infrastructure plans; House passage of the KIDS Act) rather than from
`congress_gov`. That workaround is fine but the API source is effectively dead weight until the
query is fixed.

Config (`src/collect/config.yaml`):
```
name: congress_gov
type: congress_gov
search_term: cybersecurity
days_back: 30
category_hint: legislative
```

Likely causes to check in `src/collect/fetchers/congress_gov.py`:
- The `search_term` may not be passed to the Congress.gov API request, or is passed to an
  endpoint/param that doesn't actually filter (e.g., hitting the generic recent-bills endpoint
  and ignoring the query). The Congress.gov API keyword search uses the `/search` style
  endpoint with a `query` param; confirm the fetcher targets it.
- `days_back` (30) is not being applied — bills dated back to 2025 appear, so no date filter is
  reaching the request or the post-filter.
- Note the earlier 001 verification listed bills like "HRES 1025, HR 3033, S 2975, S 1199" —
  also not obviously cyber-specific, suggesting the query never actually filtered by keyword;
  001 verified *count > 0*, not *relevance*.

## Acceptance Criteria
- [ ] Inspect the actual API request the fetcher builds; confirm whether `search_term` and
      `days_back` reach the request.
- [ ] Fix so results are keyword-scoped to cybersecurity and bounded to the recent window.
- [ ] Verify a run returns bills that are plausibly cybersecurity-related and recent.
- [ ] Consider filtering out simple resolutions (SRES/HRES ceremonial items) if the API can't
      exclude them.

## References
- Source collector: `src/collect/fetchers/congress_gov.py`
- Config: `src/collect/config.yaml` (congress_gov search_term / days_back)
- Design: `docs/superpowers/specs/2026-04-10-spectra-design.md` (Congress.gov API source)
- Related: ticket 001 (congress_gov 0-items / API-key wiring — the count fix this builds on)
