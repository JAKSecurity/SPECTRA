# SPECTRA -- Security Policy, Emerging Cyber Threats, Research & AI

AI-generated monthly cybersecurity policy digest for DoD/federal practitioners.

## Constraints

- **Public/unclassified sources only** -- no classified or CUI
- **Monthly cadence** -- policy doesn't move fast enough to justify more

## Pipeline

```
1. spectra-monthly task        -> collect, prep, curate, draft, render (single monthly run)
2. [Human reviews draft + PDF in-session]
```

### Stage details

1. **Collect**: RSS fetchers pull from configured sources into JSON files
2. **Prep**: Load + deduplicate collected items into a single prepped JSON
3. **Curate** (scheduled task): Claude categorizes items into SPECTRA sections, writes summaries, produces curated JSON and markdown draft. Runs via Claude Code subscription (no API key needed).
4. **Review**: Human reviews markdown draft before rendering
5. **Render** (on demand): Approved markdown -> PDF via reportlab
6. **Deliver**: Email (PDF attached) + Discord (#spectra-reports)

## Schedule

- **5AM on 1st of each month**: spectra-monthly scheduled task runs full pipeline
- **Last day of month**: Morning briefing note -- "SPECTRA report coming tomorrow"
- **1st of month**: Morning briefing note -- completion status or error flag

## Output Sections

1. Cover / Executive Summary
2. Policy & Compliance Updates
3. Publications & Standards
4. Threats & Incidents
5. AI & Agentic Developments
6. Legislative Highlights (significant movement only -- no full tracker)
7. Upcoming Conferences

## Tech Stack

- Python 3, feedparser, requests, reportlab
- Configuration: `src/collect/config.yaml`
- Scheduling: Claude Code scheduled tasks (spectra-monthly)
- Delivery: Gmail SMTP + Discord webhook

## Project Structure

- `src/collect/` -- Source fetcher modules and config
- `src/curate/` -- Item loading, dedup, and draft assembly
- `src/render/` -- PDF template and rendering
- `data/sources/` -- Raw fetched content by month (gitignored)
- `data/drafts/` -- Prepped items, curated items, and markdown drafts (gitignored)
- `output/` -- Final rendered PDFs (gitignored)

## Design Spec

Full design document: `docs/superpowers/specs/2026-04-10-spectra-design.md`
