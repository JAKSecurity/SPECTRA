# SPECTRA Backlog

> **Status: Complete.** All 4 phases delivered; monthly pipeline running unattended. Per-phase checklist preserved below as historical record.

## Capabilities

| ID | Name | Status | Phase | Priority | Depends On | Description |
|----|------|--------|-------|----------|------------|-------------|
| C1 | Foundation | Delivered | Phase 1 | P1 |  | Python project + collect/curate/render pipeline + first test issue (sources, dedup, markdown→PDF, scheduled task wiring) |
| C2 | Full source coverage | Delivered | Phase 2 | P1 | C1 | Federal Register, Congress.gov, CISA KEV, AI vendor/news feeds, Executive Orders, FedRAMP, The Record, RSS hygiene, monthly cadence |
| C3 | Automation & polish | Delivered | Phase 3 | P2 | C2 | Branded PDF template, relevance scoring + keyword tuning, source health monitoring with empty-source warnings |
| C4 | Integration | Delivered | Phase 4 | P1 | C3 | projects.yaml + briefing integration, scheduled monthly run, email + Discord delivery, Brain entry, TELOS Live Pulse |

## Active

| ID | Title | Status | Priority | Capability | Ticket |
|----|-------|--------|----------|------------|--------|

_(No active items — monthly pipeline running unattended; future enhancements would open new tickets here.)_

## Historical detail (pre-canonicalization)

The original phase-by-phase checklist below preserves what was delivered in each phase. Going forward, work units are tracked as `## Active` rows and capability rows above; this section is read-only.

## Phase 1: Foundation (COMPLETE)

- [x] Set up Python project (requirements.txt)
- [x] Build NIST CSRC fetcher (RSS)
- [x] Build CISA alerts/advisories fetcher (RSS)
- [x] Build RSS news fetchers (CyberScoop, Nextgov/FCW, Dark Reading)
- [x] Build source config system (config.yaml)
- [x] Build collect runner (orchestrates fetchers, handles failures)
- [x] Build curate prep pipeline (load, dedup, write prepped JSON)
- [x] Build curate scheduled task (spectra-curate, Claude Code subscription)
- [x] Build curate draft assembly (markdown from curated JSON)
- [x] Build PDF template (reportlab, SPECTRA branding)
- [x] Build render pipeline (markdown -> PDF)
- [x] Produce first test SPECTRA issue from real sources

## Phase 2: Full Source Coverage (COMPLETE)

### Added Sources
- [x] Fix NIST CSRC fetcher (switched to working publications feed)
- [x] Federal Register API fetcher (keyword-filtered)
- [x] Congress.gov API fetcher (cybersecurity bills)
- [x] CISA KEV catalog JSON fetcher
- [x] AI vendor blogs (OpenAI, DeepMind, Google AI) RSS fetchers
- [x] AI news feeds (The Verge AI, MIT Tech Review AI) RSS fetchers
- [x] The Record RSS fetcher
- [x] Executive Orders RSS fetcher (whitehouse.gov)
- [x] FedRAMP Notices + Changelog RSS fetchers

### Skipped (covered by existing sources)
- NSA cybersecurity advisories — co-published with CISA (already fetched)
- DoD CIO / CDAO — covered by Nextgov, CyberScoop, The Record
- NIST AI RMF / AISI — too infrequent, covered by news when it happens
- AI.gov — low signal, covered by AI news feeds
- NIST NVD API — CISA KEV already covers actively exploited CVEs
- Conference scrapers — Claude knowledge supplements in scheduled task
- OMB memoranda — most appear in Federal Register (already fetched)
- DISA STIG updates — quarterly, blocks automated access

### Quality Improvements
- [x] Strip HTML from RSS summaries at fetch time
- [x] Simplified to monthly cadence (no weekly collect / cross-week dedup)

## Phase 3: Automation & Polish (COMPLETE)

- [x] Refine PDF template (colored section bars, page numbers, branded footer)
- [x] Source relevance scoring and keyword tuning (scoring criteria in scheduled task prompt, consolidation guidance)
- [x] Error reporting and fetch health monitoring (_health.json report, empty source warnings)

## Phase 4: Integration (COMPLETE)

- [x] Update projects.yaml (status active, path/tracking_file set)
- [x] Morning briefing integration (last day: "report coming tomorrow", 1st: status check)
- [x] Schedule spectra-curate for 5AM on 1st of each month
- [x] Email delivery with PDF attachment (added --attach to send_email.py)
- [x] Discord delivery to dedicated SPECTRA channel (--webhook-name flag added to send_discord.py)
- [x] Quality checks in curate task (empty sections, HTML, relevance scores, source health, dupes)
- [x] Register in Brain as cross-project knowledge entry
- [x] SPECTRA nudges in reconcile-tiers (overdue digest, source health warnings)
- [x] TELOS Live Pulse integration (automatic via projects.yaml tag update)

### Setup required
- [x] Create Discord channel for SPECTRA and store webhook as DISCORD_SPECTRA_WEBHOOK in keyring
