# 201: Congress.gov resolutions link to the bill URL path

**Status**: Open  **Priority**: P3  **Type**: Bug
**Created**: 2026-10-26
**Capability**: C3

## Summary

`_bill_url` in `src/collect/fetchers/congress_gov.py` builds every House
and Senate measure's link with the bill path. Resolutions (simple,
concurrent and joint) live under their own resolution paths on
congress.gov, so a resolution kept by the relevance filter links to the
wrong page. Found by the Codex run for tickets 003 and 004 (AI Assistant
AIA-277 queue, packet spectra1), 2026-10-26.

## Acceptance

- [ ] Each measure type (HR, S, HRES, SRES, HCONRES, SCONRES, HJRES, SJRES)
      maps to its correct congress.gov path, with a test per type.

## Resolution

Implemented an explicit mapping for all eight measure types in
`src/collect/fetchers/congress_gov.py`. Unknown types emit a warning and
return a number search (`https://www.congress.gov/search?q=1234`), with
query encoding. A small ordinal helper handles `st`, `nd`, `rd`, and the
11/12/13 exceptions. Relevance filtering, paging, date windows, and key
loading are unchanged.

### URL evidence checked on 2026-10-26

The following paths are confirmed by indexed Congress.gov page content
retrieved through web search. Each page identifies the corresponding
measure type. These are search-index observations, not successful live
page fetches:

| Type | Path | Congress.gov page checked |
| --- | --- | --- |
| HR | `house-bill` | https://www.congress.gov/bill/119th-congress/house-bill/6100/titles |
| S | `senate-bill` | https://www.congress.gov/bill/119th-congress/senate-bill/391/all-info |
| HRES | `house-resolution` | https://www.congress.gov/bill/119th-congress/house-resolution/201/text/ih |
| SRES | `senate-resolution` | https://www.congress.gov/bill/119th-congress/senate-resolution/7/all-actions |
| HCONRES | `house-concurrent-resolution` | https://www.congress.gov/bill/119th-congress/house-concurrent-resolution/16/text/ih |
| SCONRES | `senate-concurrent-resolution` | https://www.congress.gov/bill/119th-congress/senate-concurrent-resolution/19/text/is?format=txt&overview=closed |
| HJRES | `house-joint-resolution` | https://www.congress.gov/bill/119th-congress/house-joint-resolution/35/text/eh?format=txt |
| SJRES | `senate-joint-resolution` | https://www.congress.gov/bill/119th-congress/senate-joint-resolution/15/committees |

Direct network fetches of all eight
`https://www.congress.gov/bill/119th-congress/<path>/1` pages returned
HTTP 403 Forbidden. The web tool also blocked opening those pages and the
eight indexed pages above. The packet's successful live-fetch requirement
therefore remains unverified; the dispatcher should confirm in an environment
that can access Congress.gov before closing this acceptance gate.

### Validation

- Added offline cases in `tests/collect/test_congress_gov.py` for each type,
  lowercase normalization, unknown-type fallback and warning, encoded search,
  and ordinals 119, 121, 122, 123, 111, 112, and 113.
- Before implementation: 12 failed, 15 passed in the fetcher's test file.
- After implementation: the full suite passed, 97 tests, using
  the repository's `.venv/bin/python -m pytest -q`.
