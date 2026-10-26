# 004: congress_gov returns bills but keyword/date filters not applied (relevance bug)
**Status**: Delivered  **Priority**: P2  **Type**: Bug
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
- [x] Inspect the actual API request the fetcher builds; confirm whether `search_term` and
      `days_back` reach the request.
- [x] Fix so results are keyword-scoped to cybersecurity and bounded to the recent window.
- [x] Verify a run returns bills that are plausibly cybersecurity-related and recent.
- [x] Consider filtering out simple resolutions (SRES/HRES ceremonial items) if the API can't
      exclude them.

## References
- Source collector: `src/collect/fetchers/congress_gov.py`
- Config: `src/collect/config.yaml` (congress_gov search_term / days_back)
- Design: `docs/superpowers/specs/2026-04-10-spectra-design.md` (Congress.gov API source)
- Related: ticket 001 (congress_gov 0-items / API-key wiring — the count fix this builds on)

## Resolution

Investigated 2026-10-26 for packet spectra1. The current OpenAPI specification
embedded at https://api.congress.gov/ lists `/bill` parameters `format`, `offset`,
`limit`, `fromDateTime` and `toDateTime`. It does not list `query` or `sort` for
this endpoint. Date parameters filter update timestamps, not legislative action
dates. The [Library of Congress bill documentation](https://github.com/LibraryOfCongress/api.congress.gov/blob/main/Documentation/BillEndpoint.md)
also distinguishes `updateDate` from `latestAction.actionDate`. Thus the old
`query` parameter did not establish relevance; recent updates could expose old
legislative actions. This corrects the Summary's unverified `/search` hypothesis.

The fetcher now requests JSON pages of 250 bills, using documented offset/date
parameters and a maximum of 40 pages. It exhausts pagination instead of stopping
at an old action (update dates and action dates differ). Reaching the cap with
more data raises an incomplete-window health error rather than publishing a
partial success. Pagination URLs are never followed; offsets are built locally
and the key remains solely in the `X-Api-Key` header.

Local filtering matches any configured term, case-insensitively, in title or
latest-action text, and requires a valid latest-action date inside the report
window (inclusive start, exclusive end). Without an explicit report window,
`days_back` now supplies the local lower bound and today is included. Config
uses an extendable `search_terms` list: cybersecurity, cyber security,
cyber-security. Legacy scalar `search_term` remains supported. Relevant
resolutions are retained; no blanket bill-type exclusion is introduced.

No environment/keyring key was readable in this sandbox. Congress fixtures
are explicitly labeled deterministic API-shaped examples, not live captures;
they cover unrelated/old/undated/exclusive-end drops, title/action matches,
pagination, term extension, day fallback and page-cap failure. The relevance
regression fails on the old code. Live validation must be rerun by the dispatcher:

```bash
/home/jak3676/src/JAKSecurity/SPECTRA/.venv/bin/python /home/jak3676/src/JAKSecurity/SPECTRA/scripts/check-source-window.py --report-month 2026-11
```

This read-only command prints counts only, loads credentials from the environment
or keyring (`ai-assistant` / `CONGRESS_GOV_API_KEY`), and exits nonzero if a source
cannot be checked. No ticket status or acceptance checkboxes changed here.

### Dispatcher follow-up

The existing `_bill_url` helper maps every House/Senate measure to a bill URL;
resolutions require their corresponding resolution URL path. This pre-existing
link defect is outside the two source-filter fixes and should receive a separate
BACKLOG item in the designated allocator checkout. This packet does not mint
IDs or edit BACKLOG.

## Live verification blocked (2026-10-26)

`scripts/check-source-window.py --report-month 2026-11` reports
"congress_gov: unavailable (no readable key)" outside any sandbox. SPECTRA's
`.venv` does not have the `keyring` package installed (it is in
`requirements.txt`), and no `CONGRESS_GOV_API_KEY` entry was visible in the
workstation keyring. Until the key is provisioned on the workstation, the
monthly run gets nothing from this source. Ticket stays open.

## Live verification (2026-10-26, after the key was stored)

Jeff stored the key in the workstation keyring (KWallet, through Secret
Service), and `keyring` is now installed in SPECTRA's `.venv`. The check
script returned `cisa_alerts: 30 items` and `congress_gov: 2 items` for
2026-10-01 to 2026-11-01: S 3315 (Health Care Cybersecurity and Resiliency
Act of 2026, latest action 2026-10-05) and HR 10238 (Cybersecurity for Small
Businesses Act of 2026, 2026-10-13). Both are on topic and in the window.
Ceremonial resolutions were not excluded by type; relevant ones are kept by
design (see Resolution). The resolution-link defect moved to ticket 201.
