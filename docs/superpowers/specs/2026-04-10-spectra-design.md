# SPECTRA Design Specification

**Security Policy, Emerging Cyber Threats, Research & AI**

Date: 2026-04-10 (revised 2026-04-11)
Status: Implemented (Phases 1-4 complete)

---

## Overview

SPECTRA is an AI-generated monthly cybersecurity policy digest covering NIST updates, federal regulations, executive orders, CISA directives, AI/agentic developments, and industry news relevant to DoD/federal cybersecurity practitioners.

The entire pipeline -- from source collection through AI curation to PDF rendering and delivery -- runs autonomously via a Claude Code scheduled task. No API keys or per-token billing required.

### Constraints

- Public/unclassified sources only -- no classified or CUI
- Monthly cadence -- policy doesn't move fast enough to justify more (daily news is handled by a separate briefing pipeline)

---

## Output Structure

SPECTRA is a monthly PDF digest with seven sections. Each section is limited to the top 20 items by relevance score.

### Section Taxonomy

| # | Section | Content | Tone |
|---|---------|---------|------|
| 1 | **Cover / Executive Summary** | Month/year, banner, 3-5 bullet key events | Brief, scannable |
| 2 | **Policy & Compliance Updates** | Federal agency actions, OMB memos, executive orders, CISA directives, FedRAMP updates, CMMC changes | Factual, action-oriented |
| 3 | **Publications & Standards** | NIST SPs/CSWPs/IRs, CISA guides, NSA info sheets, DISA STIGs, strategy docs | Descriptive, concise |
| 4 | **Threats & Incidents** | Major breaches, APT campaigns, ransomware, vulnerability disclosures, ICS advisories, KEVs | Factual, not alarmist |
| 5 | **AI & Agentic Developments** | Frontier model releases, AI safety/policy, agentic AI capabilities, AI EOs/memos/frameworks | Brief, factual |
| 6 | **Legislative Highlights** | Bills with significant movement only (committee, floor vote, signed) | Concise status updates |
| 7 | **Upcoming Conferences** | 5-10 relevant cybersecurity/AI events for the next 2-3 months | List format |

### PDF Template

- Navy banner with title, subtitle, and one-line description
- Colored section heading bars (each section has its own accent color)
- Clickable source URLs on every item
- Page numbers and branded footer on every page
- Generated via reportlab

---

## Source List (17 Active Sources)

### Government / Policy (8 sources)

| Source | Access Method | Config Key |
|--------|---------------|------------|
| NIST CSRC (cybersecurity insights blog) | RSS | `nist_csrc` |
| CISA Alerts & Advisories | RSS | `cisa_alerts` |
| CISA KEV Catalog | JSON API | `cisa_kev` |
| Federal Register (cybersecurity keyword) | REST API | `federal_register` |
| Congress.gov (cybersecurity bills) | REST API | `congress_gov` |
| Executive Orders (whitehouse.gov) | RSS | `executive_orders` |
| FedRAMP Notices | RSS | `fedramp_notices` |
| FedRAMP Changelog | RSS | `fedramp_changelog` |

### Industry / News (4 sources)

| Source | Access Method | Config Key |
|--------|---------------|------------|
| CyberScoop | RSS | `cyberscoop` |
| Nextgov/FCW | RSS | `nextgov` |
| Dark Reading | RSS | `dark_reading` |
| The Record (Recorded Future) | RSS | `the_record` |

### AI / Agentic (5 sources)

| Source | Access Method | Config Key |
|--------|---------------|------------|
| OpenAI Blog | RSS | `openai_blog` |
| Google AI Blog | RSS | `google_ai_blog` |
| DeepMind Blog | RSS | `deepmind_blog` |
| The Verge / AI | RSS | `the_verge_ai` |
| MIT Technology Review / AI | RSS | `mit_tech_review_ai` |

### Sources Evaluated and Skipped

These sources were evaluated during Phase 2 and deliberately excluded:

| Source | Reason |
|--------|--------|
| NSA Cybersecurity | Co-published with CISA (already captured); site blocks automated access |
| DoD CIO / CDAO | Covered by Nextgov, CyberScoop, The Record; site blocks automated access |
| NIST AI RMF / AISI | Too infrequent; major updates covered by news feeds |
| AI.gov | Low signal; covered by AI news feeds |
| NIST NVD API | CISA KEV already covers actively exploited CVEs |
| OMB Memoranda | Most appear in Federal Register (already fetched) |
| DISA STIGs | Quarterly; blocks automated access |
| Anthropic Blog | No public RSS feed |
| SC Media | Cloudflare-blocked |
| Conference scrapers | Claude's knowledge supplements in scheduled task |

### Exclusions (by policy)

- No classified or CUI feeds
- No vendor marketing blogs
- No social media sources
- No paywalled sources

---

## Pipeline Architecture

Single monthly pipeline. All stages run in one scheduled task session on the 1st of each month at 5AM. The operator reviews the draft in-session before render and delivery.

### Stages

```
spectra-curate scheduled task (5AM, 1st of month)
  |
  +--> Collect (17 sources)     --> data/sources/YYYY-MM/*.json + _health.json
  +--> Prep (load + dedup)      --> data/drafts/prepped_YYYY-MM.json
  +--> Curate (categorize/summarize/score) --> data/drafts/curated_YYYY-MM.json
  +--> Draft assembly           --> data/drafts/YYYY-MM-SPECTRA.md
  +--> Quality checks           --> verify sections, scores, HTML, dupes
  +--> [Human review]
  +--> Render                   --> output/YYYY-MM-SPECTRA.pdf
  +--> Deliver                  --> Email (with PDF) + Discord (#spectra-reports)
```

#### Stage 1: Collect

- **What it does:** Each fetcher module pulls from one configured source, writes structured JSON to `data/sources/YYYY-MM/`
- **Design principles:**
  - Config-driven: `src/collect/config.yaml` defines URLs, keywords, API params, active fetchers
  - Fault-tolerant: individual fetcher failures are logged but don't block other fetchers
  - HTML stripping at fetch time
  - Health monitoring: `_health.json` written with per-source status, item counts, and warnings
- **Fetcher types:**
  - `rss` -- Generic RSS/Atom fetcher (feedparser)
  - `federal_register` -- Federal Register REST API with keyword search
  - `cisa_kev` -- CISA Known Exploited Vulnerabilities JSON catalog
  - `congress_gov` -- Congress.gov API with keyword search

#### Stage 2: Prep

- **What it does:** Loads all items from `data/sources/YYYY-MM/`, deduplicates by URL, writes a single clean JSON file
- **Output:** `data/drafts/prepped_YYYY-MM.json`
- **Entry point:** `scripts/curate.sh` or `python -m src.curate.curate`

#### Stage 3: Curate (AI)

- **What it does:** Claude reads the prepped JSON and for each item: assigns to one SPECTRA section, writes a 2-3 sentence summary, scores relevance 1-10. Consolidates duplicate stories. Adds 5-10 upcoming conferences from Claude's knowledge.
- **Relevance scoring criteria:**
  - 9-10: Directly affects DoD/federal cyber operations or compliance
  - 7-8: Significant for federal practitioners but not immediately actionable
  - 5-6: General cybersecurity interest, indirect federal relevance
  - 3-4: Tangential (only included if month is light on content)
  - 1-2: Not relevant (excluded)
- **Output:** `data/drafts/curated_YYYY-MM.json`

#### Stage 4: Draft Assembly

- **What it does:** Assembles curated items into markdown with executive summary (top 5 by relevance), section headings, source URLs, and item limits (top 20 per section)
- **Output:** `data/drafts/YYYY-MM-SPECTRA.md`
- **Entry point:** `scripts/curate-draft.sh` or `src.curate.draft.assemble_draft()`

#### Stage 5: Quality Checks

Automated checks before presenting draft for review:
- No empty sections
- No HTML tags in summaries
- Relevance scores in valid range (1-10)
- Source health report reviewed (failed/empty sources flagged)
- No duplicate titles across sections

#### Stage 6: Render

- **What it does:** Markdown draft to branded PDF via reportlab
- **Output:** `output/YYYY-MM-SPECTRA.pdf`
- **Entry point:** `scripts/render.sh` or `python -m src.render.render`

#### Stage 7: Deliver

- **Email:** PDF attached, markdown body (via AI Assistant `send_email.py --attach`)
- **Discord:** Posted to #spectra-reports channel (via AI Assistant `send_discord.py --webhook-name DISCORD_SPECTRA_WEBHOOK`)

---

## Integration with AI Assistant

SPECTRA integrates with the central AI Assistant system:

- **projects.yaml:** Registered as `spectra` (active, Phase 4 complete)
- **Morning briefing:** Last day of month: "SPECTRA report coming tomorrow." 1st of month: completion status or error note.
- **Reconciler nudges:** `spectra_overdue` (digest not produced by 2nd of month), `spectra_source_health` (sources failed or empty)
- **TELOS Live Pulse:** Linked to M1 (translate expertise into policy) via `telos-m1` tag
- **Brain:** Architecture decision registered as `2026-04-11-spectra-pipeline-architecture`

---

## Directory Structure

```
SPECTRA/
+-- CLAUDE.md                   Project context for Claude Code
+-- requirements.txt            Python dependencies
+-- docs/
|   +-- BACKLOG.md              Phase tracking and backlog
|   +-- superpowers/
|       +-- specs/              Design documents
+-- src/
|   +-- collect/
|   |   +-- config.yaml         Source URLs, types, category hints
|   |   +-- runner.py           Orchestrates fetchers, writes health report
|   |   +-- fetchers/
|   |       +-- base.py         Base fetcher class
|   |       +-- rss.py          Generic RSS/Atom fetcher
|   |       +-- federal_register.py
|   |       +-- cisa_kev.py
|   |       +-- congress_gov.py
|   +-- curate/
|   |   +-- curate.py           Load items, deduplicate, prep
|   |   +-- draft.py            Assemble markdown from curated JSON
|   +-- render/
|       +-- render.py           Markdown to PDF via reportlab
+-- data/
|   +-- sources/YYYY-MM/        Raw fetched JSON (one file per source)
|   +-- drafts/                 Prepped, curated, and markdown drafts
+-- output/                     Final rendered PDFs
+-- scripts/
|   +-- collect.sh              Run collect stage
|   +-- curate.sh               Run prep stage
|   +-- curate-draft.sh         Run draft assembly
|   +-- render.sh               Run render stage
+-- tests/                      59 tests (pytest)
    +-- collect/                Fetcher and runner tests
    +-- curate/                 Prep and draft assembly tests
    +-- render/                 Parse and PDF generation tests
```

---

## Tech Stack

- **Language:** Python 3
- **RSS/Feed parsing:** feedparser
- **HTTP requests:** requests
- **PDF generation:** reportlab
- **Configuration:** YAML (PyYAML)
- **Testing:** pytest (59 tests)
- **AI curation:** Claude Code scheduled task (subscription -- no API key or per-token billing)
- **Delivery:** Gmail SMTP (email with attachments), Discord webhooks
- **Scheduling:** Claude Code scheduled tasks (cron: 5AM on 1st of month)

---

## Delivery History

### Phases 1-4: Complete (2026-04-10 to 2026-04-11)

- Phase 1: Foundation -- end-to-end pipeline with 5 RSS sources, 34 tests
- Phase 2: Full source coverage -- 17 sources (RSS + 3 APIs), HTML stripping, 59 tests
- Phase 3: Polish -- colored PDF template, relevance scoring, health monitoring
- Phase 4: Integration -- scheduled task, email/Discord delivery, briefing reminders, Brain, nudges
