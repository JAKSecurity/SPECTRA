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
