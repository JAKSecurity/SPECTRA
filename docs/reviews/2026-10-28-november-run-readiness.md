# November 2026 run readiness — checked October 28

**Verdict: the November 1 run is likely to produce a usable but incomplete draft if today's access holds: 289 October items collect and 286 survive preparation, with two blocked feeds, one stale feed, and a confirmed preparation data-loss defect.**

This is readiness evidence for the Security Policy, Emerging Cyber Threats,
Research & AI (SPECTRA) November issue, not an approved monthly draft. The
content window is **2026-10-01 inclusive to 2026-11-01 exclusive**. Collection
completed at 2026-10-28 05:33:05 Coordinated Universal Time (UTC); separate
feed-body diagnostics began at 05:32:54 UTC. October is still in progress.
This check cannot guarantee November 1 network access, scheduler execution,
or model-backed curation.

## Live source results

The normal collection command returned exit status 0: **17 attempted, 15
successful, 2 errors, 1 successful-but-empty, 289 saved items**. A successful
process exit therefore does not mean every source succeeded.

For Really Simple Syndication (RSS) feeds, “Observed” and oldest/newest refer
to the full feed in a separate, near-contemporaneous request. “October saved”
is the actual collector output; all 289 saved items have valid October dates.
For the three application programming interface (API) sources, observed counts
and date ranges below refer to the filtered collector output, not the full
upstream catalog or all scanned bills. Errors have unknown upstream counts,
not verified zero-item feeds. A dash means no usable date was available.

| Source | Status | Observed | October saved | Oldest observed date | Newest observed date |
| --- | --- | ---: | ---: | --- | --- |
| `nist_csrc` | OK | 40 | 4 | 2024-10-08 | 2026-10-27 |
| `cisa_alerts` | OK; short feed history | 30 | 30 | 2026-10-20 | 2026-10-27 |
| `cyberscoop` | OK; short feed history | 10 | 10 | 2026-10-23 | 2026-10-27 |
| `nextgov` | OK | 25 | 23 | 2026-09-29 | 2026-10-27 |
| `dark_reading` | OK; short feed history | 50 | 50 | 2026-10-15 | 2026-10-27 |
| `the_record` | OK; one-day feed history | 5 | 5 | 2026-10-27 | 2026-10-27 |
| `openai_blog` | OK | 1,331 | 64 | 2015-12-11 | 2026-10-27 |
| `google_ai_blog` | OK; redirect followed | 20 | 5 | 2026-09-02 | 2026-10-26 |
| `deepmind_blog` | OK | 100 | 8 | 2025-11-18 | 2026-10-27 |
| `the_verge_ai` | Error: Hypertext Transfer Protocol (HTTP) 403 | unknown | 0 | — | — |
| `mit_tech_review_ai` | Error: HTTP 403 | unknown | 0 | — | — |
| `executive_orders` | OK | 30 | 12 | 2026-09-08 | 2026-10-23 |
| `fedramp_notices` | **All stale; zero October items** | 16 | 0 | 2026-02-18 | 2026-07-22 |
| `fedramp_changelog` | OK collection; **4 become 1 in prep** | 98 | 4 | 2025-01-12 | 2026-10-21 |
| `federal_register` | OK; filtered output | 42 | 42 | 2026-10-01 | 2026-10-27 |
| `cisa_kev` | OK; filtered output | 30 | 30 | 2026-10-01 | 2026-10-27 |
| `congress_gov` | OK; filtered output | 2 | 2 | 2026-10-05 | 2026-10-13 |

All 12 accessible RSS responses were HTTP 200 and parsed as RSS 2.0 without
parser errors. Every entry had a parsed publication date; no updated-only
entries explained an empty result. The two HTTP 403 failures repeated in the
independent diagnostics. Their cause could be publisher or network access
controls; this does not establish retirement or a replacement URL.

The Google artificial intelligence (AI) feed redirects successfully to
`https://blog.google/innovation-and-ai/technology/ai/rss/`. The existing
transport follows it, so no configuration repair is needed. Federal Risk and
Authorization Management Program (FedRAMP) Notices is reachable and contains
16 dated entries, all before October. That demonstrates stale feed contents,
not necessarily that the program published no notices this month.

Congress.gov credentials were readable through the existing environment/keyring
resolution path. No key was printed, copied, or placed in a URL. Live results:

- S 3315, *Health Care Cybersecurity and Resiliency Act of 2026*, action date
  October 5; `https://www.congress.gov/bill/119th-congress/senate-bill/3315`.
- HR 10238, *Cybersecurity for Small Businesses Act of 2026*, action date
  October 13; `https://www.congress.gov/bill/119th-congress/house-bill/10238`.

This confirms current collection for SPECTRA-003 (CISA retry) and SPECTRA-004
(Congress filtering). Cybersecurity and Infrastructure Security Agency (CISA)
Known Exploited Vulnerabilities (KEV) collection also succeeds. Neither returned
Congress measure is a resolution, so this check does not close SPECTRA-201
(resolution links)'s separate live-link acceptance gate.

## Preparation, duplicates, and deterministic assembly

`src.curate.curate` successfully loaded the scratch source directory, skipped
its health receipt, and wrote **286 prepped items from 289 collected items**.
All collected items have identifiers, titles, URLs, and publication dates.
Six have empty summaries: four from DeepMind and two from the Federal Register.
These need source-page reading during curation; they are not preparation errors.

**The three removed rows are not duplicate stories.** All four October
FedRAMP changelog entries point to `https://www.fedramp.gov/changelog`, but have
distinct feed identifiers ending in `/98`, `/97`, `/96`, and `/95`:

| Date | Feed identifier suffix | Distinct update | Prep result |
| --- | --- | --- | --- |
| 2026-10-21 | `/98` | Marketplace display of 20x Pilot certifications | Kept |
| 2026-10-15 | `/97` | Request for Comments (RFC) 0036: 20x Class D Cloud-Hosted Pilot Requirements | Dropped |
| 2026-10-14 | `/96` | RFC 0035: Cryptographic Module Use Updates | Dropped |
| 2026-10-08 | `/95` | Fiscal year 2026 results and fiscal year 2027 outlook blog announcement | Dropped |

`src/collect/fetchers/rss.py` hashes the link for the item identifier, so these
four entries also receive the same generated identifier.
`src/curate/curate.py:deduplicate` keeps only the first occurrence of a URL.
A complete repair needs coordinated entry identity and deduplication behavior,
with a recorded-response regression covering these four distinct entries and
true repeated entries. It cannot safely be repaired by substituting the feed
identifier as a reader link: those identifiers were not verified as article
pages. This is documented for the dispatcher rather than expanding this
source-repair packet into a shared deduplication policy change.

There were **no exact URL duplicates across different sources**. One exact
normalized-title match across sources remains after preparation:
*Gemini 4 Argon: built to solve your hardest problems* appears in both
`deepmind_blog` and `google_ai_blog`, with different URLs. Model-backed curation
must consolidate that story. Repeated CISA alert titles and Federal Register
notice titles also occur at distinct URLs; equal titles alone do not establish
duplicate documents and should not be automatically discarded.

`src.curate.draft.assemble_draft` also completed a deterministic smoke check
using the three existing curated test fixtures and a November label. It emitted
three section items. This only checks assembly mechanics: raw prepped items
have category hints, not the curated `section` and relevance fields required
by assembly. No live curation, scoring, or monthly draft was fabricated.

## Fixes and scope decisions

**No production source or configuration change was made.** No changed URL,
date parser failure, or source-filter regression was demonstrated. Existing
CISA retry, Congress filtering, and resolution mapping code remains intact.
The recorded-response Congress examples in `tests/collect/fixtures/` are
synthetic API-shaped fixtures, not captured live bills; the live Congress
result above is separate evidence.

The access failures and stale feed need follow-up rather than guessed replacement
feeds. The FedRAMP preparation loss is a confirmed local defect, deferred because
its repair changes shared identity/deduplication behavior rather than a source
URL or date filter. No feed was dropped or added, no credential was provisioned,
and no automation, tracker, or delivery setting was changed.

## For Jeff and the dispatcher

1. **Track and repair FedRAMP preparation loss.** Three distinct October updates
   disappear before curation. Preserve the genuine landing-page links while
   making entry identity and deduplication distinguish these updates.
2. **Recheck access from the scheduled-run environment** for The Verge and MIT
   Technology Review feeds. Both failed twice here. Decide on any replacement
   or removal separately; other AI feeds supplied 77 October items today.
3. **Review FedRAMP Notices freshness.** Its latest feed entry is July 22. The
   separate changelog provides October material but does not prove notices
   coverage. A new feed or source requires an explicit decision.
4. **Decide whether feed snapshots meet the coverage expectation.** CISA Alerts,
   CyberScoop, Dark Reading, and The Record begin October 20, 23, 15, and 27
   respectively. A once-monthly fetch cannot recover earlier items absent from
   these responses, and more may roll off before November 1. Archive retrieval
   or more frequent collection would change the collection design; neither
   was introduced here. “Usable” must not be read as comprehensive October
   coverage.
5. **Watch Federal Register volume.** `src/collect/fetchers/federal_register.py`
   requests only one page of 50 results without pagination. Today's response
   yielded 42; no overflow was demonstrated. More matches before month-end
   could exceed this limit. Record this as a capacity risk, not a measured
   November failure.
6. Reconcile SPECTRA-201 (resolution links) only against its outstanding live-link
   evidence: implementation is present, while `docs/BACKLOG.md` and its ticket
   still say Open. This check provides no new resolution-link verification.

No ticket identifiers were allocated, and no tracking files were edited.

## Reproduction and validation

The worktree has no `.venv`; commands used the main checkout's `.venv/bin/python`
with this worktree as the working directory. In the commands below,
`SPECTRA_PYTHON` denotes that interpreter. Scratch files and test temporary files
stay inside ignored `output/november-readiness/`, never `data/`.

```bash
export TMPDIR="$PWD/output/november-readiness"
export PYTHONDONTWRITEBYTECODE=1
"$SPECTRA_PYTHON" -m src.collect.runner src/collect/config.yaml \
  output/november-readiness/spectra-sources --report-month 2026-11
"$SPECTRA_PYTHON" -m src.curate.curate \
  output/november-readiness/spectra-sources/2026-11 \
  output/november-readiness/prepped_2026-11.json
test -s docs/reviews/2026-10-28-november-run-readiness.md && \
  "$SPECTRA_PYTHON" -m pytest -q
```

Scratch evidence includes `spectra-sources/2026-11/_health.json`, the 15 source
files, `prepped_2026-11.json`, `feed-audit.json`, accessible RSS bodies under
`responses/`, and `assembly-smoke-fixture.md`, all beneath
`output/november-readiness/`. These are ignored and ephemeral; the observations
needed for review are retained in this document.

Collection and preparation exited successfully; assembly smoke passed.
Acceptance command passed: the report is nonempty and **97 tests passed**.
No ambient temporary-directory Git interference was observed.
The suite's existing renderer tests may create temporary fixture documents;
no monthly Portable Document Format (PDF) report was rendered, no email or
Discord message was sent, and no additional model-backed curation or paid
service was used.
