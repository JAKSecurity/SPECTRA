# November collection rehearsal — October 28, 2026

**Verdict: collection and preparation work end to end; not ready to certify complete October coverage for November 1 at 05:00.** All 17 enabled sources completed without a fetch error, including both previously blocked feeds. Preparation retained **362 of 362 items**. Resolve or explicitly disclose the remaining feed-history limits and the zero notices source before treating the issue as a complete monthly digest.

## Method and timing

Ran October 28 at 20:14:46–20:15:40 America/New_York, corresponding to October 29 at 00:14:46–00:15:40 Coordinated Universal Time (UTC). Collection took **54.380 seconds**; collection plus preparation and local checks took **54.392 seconds** (including the credential-availability check). This is a snapshot before October 29–31 content exists, not a prediction of November 1 availability.

Used the native repository's existing virtual environment to run this worktree's production code. Invoked `src.collect.runner.main()` with the exact arguments below, preserving configuration, request behavior, core-source retry behavior, and source-file saving:

```text
config_path: src/collect/config.yaml
output_base: .sandbox-data/november-rehearsal/sources
--report-month 2026-11
```

The issue-month argument selected `2026-10-01 <= published < 2026-11-01` through `src/collect/runner.py:17`. All collection files, `_health.json`, preparation output, and a credential-free measurement summary were confined to the new `.sandbox-data/november-rehearsal/` folder. A temporary in-memory driver filtered console output to counts/statuses and disabled logging to avoid emitting request internals or exception messages; no fetcher or runner implementation was patched. No source diagnostic requests were added. This means page-cap log messages were not retained; coverage conclusions below distinguish saved-date evidence from inferred truncation.

Read `_health.json` and all 17 saved source files, then ran the README's preparation implementation, `src.curate.curate.prep_items()`, with the collected issue directory and `.sandbox-data/november-rehearsal/prepped_2026-11.json`. This only loads and deduplicates; it performs no model-backed curation. No writes went to `data/` or `output/`. No curation, rendering, delivery, scheduler changes, source changes, or tracker edits occurred. The throwaway folder was removed after extracting these results.

## Source comparison

The comparison column is the **October count** in `docs/plans/2026-10-28-november-run-preflight.md`, not that report's July/August/September columns. A drop flag requires the new count to be strictly less than two thirds of the earlier numeric count. No source meets that drop threshold, and none failed. Earlier failures have unknown counts, not zeros. Dates below are publication dates of saved in-window items, not bounds of the entire publisher archive.

`ok` is the runner's literal source health status. A zero source can still be marked `ok`; the aggregate health separately counts it as empty. Short-history flags are coverage concerns, not fetch failures.

| Enabled source | Items | Earliest published | Latest published | Health | Preflight October count | Flag / likely cause or comparison |
|---|---:|---|---|---|---:|---|
| `nist_csrc` | 4 | 2026-10-01 | 2026-10-27 | ok | 4 | Unchanged. Configured cybersecurity blog, not a complete standards inventory. |
| `cisa_alerts` | 30 | 2026-10-20 | 2026-10-28 | ok | 30 | Short history persists: Cybersecurity and Infrastructure Security Agency (CISA) feed retains recent advisories. Equal counts do not establish early-month coverage. |
| `cyberscoop` | 50 | 2026-10-08 | 2026-10-28 | ok | 10 | Fivefold increase after paging. Earliest saved item is still October 8; configured five-page ceiling leaves October 1–7 coverage unverified. Result is consistent with exhausting five ten-item pages; request/page logs were not captured. |
| `nextgov` | 25 | 2026-10-06 | 2026-10-28 | ok | 25 | Short-history risk persists; no evidence here of coverage for October 1–5. |
| `dark_reading` | 50 | 2026-10-15 | 2026-10-28 | ok | 50 | Short-history risk persists; recent 50-item feed does not certify the earlier month. |
| `the_record` | 5 | 2026-10-28 | 2026-10-28 | ok | 5 | Short-history risk persists; all saved items cover one day. |
| `openai_blog` | 67 | 2026-10-01 | 2026-10-28 | ok | 66 | One additional item; no drop. |
| `google_ai_blog` | 5 | 2026-10-02 | 2026-10-26 | ok | 5 | Unchanged; earlier preflight attributed low volume to supplied feed content, with no demonstrated parsing defect. Not a drop against this baseline. |
| `deepmind_blog` | 9 | 2026-10-06 | 2026-10-28 | ok | 9 | Unchanged. |
| `the_verge_ai` | 10 | 2026-10-27 | 2026-10-28 | ok | Unknown: fetch failed | Recovered under the merged client identity; short history remains (two days of saved content). |
| `mit_tech_review_ai` | 10 | 2026-10-20 | 2026-10-28 | ok | Unknown: fetch failed | Recovered under the merged client identity; short history remains. |
| `executive_orders` | 13 | 2026-10-02 | 2026-10-28 | ok | 12 | One additional item; feed includes presidential actions beyond executive orders. |
| `fedramp_notices` | 0 | — | — | ok; empty warning | 0 | **ZERO.** Likely publication silence or stale feed/index. Earlier preflight found latest notice July 22; this run confirms no saved October items, but did not re-inspect the publisher index or distinguish silence from staleness. |
| `fedramp_changelog` | 4 | 2026-10-08 | 2026-10-21 | ok | 4 | Unchanged; four distinct entries survive preparation despite a shared landing page. Federal Risk and Authorization Management Program (FedRAMP) source. |
| `federal_register` | 46 | 2026-10-01 | 2026-10-28 | ok | 46 | Unchanged. Current collection is in-window; historical baseline defects were not revisited. |
| `cisa_kev` | 32 | 2026-10-01 | 2026-10-28 | ok | 30 | Two additional Known Exploited Vulnerabilities (KEV) catalog entries. |
| `congress_gov` | 2 | 2026-10-05 | 2026-10-13 | ok | 2 | Credentials were readable through the existing environment/keyring lookup; production collection returned two qualifying items. This is verified output, not an unavailable source or assumed zero. |

Health summary: **17 total; 17 succeeded; 0 failed; 1 empty; 362 items**. Each file's item count matched its health entry. All 362 publication dates fall within the requested window. Congress.gov credential values, request headers, and exception text were never emitted by the rehearsal driver or copied into this report. If the unattended environment lacks readable credentials, Congress.gov must instead be reported as **unavailable, not a verified zero**; this run cannot certify scheduler credential access.

## Preparation result

**362 raw items → 362 prepped items; 0 duplicates removed.** The earlier preflight retained 298 items. The 64-item increase consists of CyberScoop +40, recovered Verge +10, recovered MIT Technology Review +10, OpenAI +1, presidential actions +1, and CISA KEV +2. Diagnostic or alternate-source items were not mixed into the production result.

## Collection-path findings and proposed fixes

No source code was changed. The production path now runs successfully, but its health reporting does not certify content completeness:

1. **Feed-history coverage remains bounded.** `src/collect/config.yaml` restricts CyberScoop to five pages; `src/collect/fetchers/rss.py:53` applies the bound, and `src/collect/fetchers/rss.py:85` only logs when it is reached. The saved collection starts October 8. `src/collect/runner.py:64` records `ok` without a completeness field, so `_health.json` cannot distinguish a potentially capped result from complete history. Proposed fix: expose page count, cap reached, and whether a dated page crossed the window boundary as structured health metadata. Establish enough supported CyberScoop history to cross October 1, with a bounded explicit failure/warning if the limit is reached. Merely increasing a cap does not prove complete history. Add regression coverage for a cap reached before the date boundary and for its propagation into health.
2. **Other rolling feeds still lack archive recovery.** `src/collect/fetchers/rss.py:53` uses one page when a source is not configured for paging. Saved bounds for CISA advisories, Nextgov, Dark Reading, The Record, The Verge, and MIT Technology Review remain late in October. The earlier preflight already documented this concern; the merged client identity recovers access, not history. Proposed fix: establish a supported archive or pagination path per affected publisher, with identity deduplication and an explicit window-boundary check. Do not apply a guessed paging parameter across publishers. This rehearsal did not prove an exact missing-item count or validate any alternative archive.
3. **Missing Congress.gov credentials masquerade as a successful empty collection.** `src/collect/fetchers/congress_gov.py:81` returns an empty result when no key is readable; `src/collect/runner.py:64` then labels it `ok`. This is a code-inspected conditional defect, **not triggered here**, because credentials were available. The checker already distinguishes unavailable sources at `scripts/check-source-window.py:43`. Proposed fix: carry an explicit unavailable status through the production fetcher/runner/health path, retain an unknown item count, and test the missing-key case end to end. Do not convert missing credentials into legislative inactivity.

For FedRAMP notices, the evidence does not justify a parser fix. Recheck an authoritative publisher index/feed at month close and retain the zero-source warning unless newer notices are established.

## Validation and dispatcher facts

- Before collection: **138 tests passed in 0.25 seconds** using the packet's native virtual-environment interpreter and `-m pytest -q`. No temporary-directory Git interference occurred.
- Final acceptance: **138 tests passed in 0.20 seconds**; the report existence check also passed, and the throwaway folder was confirmed absent. Command: `test -s docs/plans/2026-10-28-november-collect-rehearsal.md && /home/jak3676/src/JAKSecurity/SPECTRA/.venv/bin/python -m pytest -q`.
- Only this report is a deliverable. Git mutations and tracker edits are left to the dispatcher. No new ticket identifiers were allocated.
- Dispatcher: retain successful transport/paging evidence, keep the monthly-history gap and notices zero visible, and check for existing ownership before recording follow-up work for structured completeness and unavailable-source health. This rehearsal neither opens nor closes repair tickets.
- For Jeff: the 05:00 run can collect and prepare with the present code and this environment's credentials, but complete monthly coverage is not established. Any acceptance of limited coverage or change to collection cadence/archive strategy remains a separate decision. The scheduler itself was not exercised.
