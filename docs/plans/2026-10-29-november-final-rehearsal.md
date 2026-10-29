# November final rehearsal — October 29, 2026

**Combined collection and preparation pass: 394 raw items → 394 prepared items; 17 successful sources, including five partial sources, no errors and no unavailable sources.** The extra history works with the new saved-file metadata. Complete October coverage remains unproven for five rolling feeds. The source checker now reports those coverage gaps using the same criteria as collection health.

## Method and timing

Ran October 28, 2026 at 22:38:37–22:39:33 America/New_York (October 29 at 02:38:37–02:39:33 Coordinated Universal Time (UTC)). Production collection took 56.656 seconds; collection, preparation and local validation took 56.663 seconds. This is a snapshot before month end, not an execution of the November 1 scheduler.

The initial full suite passed **154 tests in 0.29 seconds**. Used the native repository's existing virtual environment to execute this worktree's production entry points. A temporary in-memory driver invoked `src.collect.runner.main()` with the following argument shape, then `src.curate.curate.main()` using the README's source-directory/output-file preparation interface:

```text
python -m src.collect.runner src/collect/config.yaml <temporary-root>/sources --report-month 2026-11
python -m src.curate.curate <temporary-root>/sources/2026-11 <temporary-root>/prepped.json
```

The throwaway root was allocated with `tempfile.mkdtemp(prefix="spectrafinal-")` under the system temporary directory, outside this worktree. Nothing was collected into `data/` or `output/`. The driver suppressed console and logging output so request internals and exception messages could not enter the run transcript; it did not patch collection, request, retry, save or preparation behavior. Only credential-free measurements were printed. The existing Congress.gov application programming interface (API) authentication path sends its key in the `X-Api-Key` header; no credential values or headers were printed or copied here.

Read `_health.json` and every saved source file. All 17 files' status and coverage fields matched their health entries, all item counts matched (unavailable would have an unknown health count and an empty saved item list), and every saved publication date fell within `2026-10-01 <= published < 2026-11-01`.

## Source comparison

Previous counts come from `docs/plans/2026-10-28-november-collect-rehearsal.md`, which collected 362 items. Its health marked all sources `ok` and did not expose structured coverage, so prior page counts/cap/boundary values are **not available**, rather than false or zero. Current values below are directly observed saved metadata; `unknown` represents JSON `null`. Date bounds refer only to saved in-window items. A boundary is reached only after seeing a dated item strictly before October 1; it need not coincide with the earliest saved October item.

| Source | Status | Count | Earliest | Latest | Pages | Cap reached | Window start reached | Previous count | Change |
|---|---|---:|---|---|---:|---|---|---:|---:|
| `nist_csrc` | ok | 4 | 2026-10-01 | 2026-10-27 | 1 | false | true | 4 | +0 |
| `cisa_alerts` | partial | 30 | 2026-10-20 | 2026-10-28 | 1 | false | false | 30 | +0 |
| `cyberscoop` | ok | 65 | 2026-10-01 | 2026-10-29 | 8 | false | true | 50 | +15 |
| `nextgov` | partial | 25 | 2026-10-06 | 2026-10-29 | 1 | false | false | 25 | +0 |
| `dark_reading` | partial | 50 | 2026-10-15 | 2026-10-28 | 1 | false | false | 50 | +0 |
| `the_record` | partial | 5 | 2026-10-28 | 2026-10-28 | 1 | false | false | 5 | +0 |
| `openai_blog` | ok | 67 | 2026-10-01 | 2026-10-28 | 1 | false | true | 67 | +0 |
| `google_ai_blog` | ok | 5 | 2026-10-02 | 2026-10-26 | 1 | false | true | 5 | +0 |
| `deepmind_blog` | ok | 9 | 2026-10-06 | 2026-10-28 | 1 | false | true | 9 | +0 |
| `the_verge_ai` | partial | 10 | 2026-10-27 | 2026-10-28 | 1 | false | false | 10 | +0 |
| `mit_tech_review_ai` | ok | 27 | 2026-10-02 | 2026-10-28 | 4 | false | true | 10 | +17 |
| `executive_orders` | ok | 13 | 2026-10-02 | 2026-10-28 | 1 | false | true | 13 | +0 |
| `fedramp_notices` | ok | 0 | — | — | 1 | false | true | 0 | +0 |
| `fedramp_changelog` | ok | 4 | 2026-10-08 | 2026-10-21 | 1 | false | true | 4 | +0 |
| `federal_register` | ok | 46 | 2026-10-01 | 2026-10-28 | unknown | unknown | unknown | 46 | +0 |
| `cisa_kev` | ok | 32 | 2026-10-01 | 2026-10-28 | unknown | unknown | unknown | 32 | +0 |
| `congress_gov` | ok | 2 | 2026-10-05 | 2026-10-13 | unknown | unknown | unknown | 2 | +0 |

Health totals: **17 sources; 17 succeeded; 5 partial; 0 failed; 0 unavailable; 1 empty; 394 items**. Successful totals intentionally include partial sources. No configured page cap was reached.

CyberScoop increases **50 → 65**, recovering the October 1 boundary in eight pages under its ten-page cap. MIT Technology Review artificial intelligence (AI) increases **10 → 27**, crossing the boundary in four pages under its six-page cap; its earliest October item is October 2 because earlier fetched entries are September publications. These match the recovered counts in `docs/plans/2026-10-28-feed-history.md`. The net increase is exactly 32 items, all from those two sources.

The five partial sources are Cybersecurity and Infrastructure Security Agency (CISA) advisories, Nextgov, Dark Reading, The Record and The Verge AI. Each has one fetched page, no cap reached and `window_start_reached=false`. This is the new health making existing short history visible, not five new transport failures. Nextgov and CyberScoop now include October 29 publication dates even though collection occurred October 28 in local time; date strings remain within the issue window. Equal counts across runs do not prove identical item identities or no new publisher activity.

Federal Risk and Authorization Management Program (FedRAMP) notices remains an `ok` zero with a crossed boundary and an empty-source warning. This establishes no in-window saved notices, not whether publication silence or a stale index explains it. Federal Register, CISA Known Exploited Vulnerabilities (KEV) and Congress.gov report unknown coverage metadata; `ok` with unknown coverage does not certify complete history.

## Preparation and consumer checks

**394 raw → 394 prepared; 0 duplicates removed.** Source attribution and all four FedRAMP changelog entries survive preparation. `src/curate/curate.py` loads each non-underscore source file's `items` list and ignores added top-level metadata. `_health.json` is excluded, so its null unavailable count cannot be mistaken for an item list. The production unavailable saved-file contract is `status="unavailable"`, `items=[]`; no preparation implementation change was needed.

Reviewed consumers in `src/collect/runner.py`, `src/collect/fetchers/base.py`, `src/curate/curate.py`, `scripts/check-source-window.py`, and the monthly automation instructions. Runner printing, totals and saved-file serialization already handle partial/unavailable sources. Preparation's output schema remains unchanged for downstream draft assembly and rendering. The automation explicitly instructs the agent to review `_health.json`; it does not implement a fixed parser that rejects the new status fields. This rehearsal covers collection/preparation, not model-backed curation, rendering or human review.

Added an offline collection-to-preparation integration test in `tests/collect/test_coverage_health.py`: real source-file saving combines a partial feed with a missing-key Congress.gov source, then preparation loads the directory containing health's null count and produces only the two usable feed items. It also checks that coverage metadata does not leak into prepared item records. The live environment had a readable key, so the unavailable path is verified offline rather than claimed as a live outcome.

Fixed `scripts/check-source-window.py` to label page-cap or unreached-window results `partial`, including zero-item partial results, and honor an explicit fetcher unavailable status as an unknown count. Existing source-line structure, item/date reporting, configuration order, single fetch attempt, read-only behavior and exit codes remain: failed/unavailable returns 1; ok/zero/partial returns 0. Summary retains its existing totals and appends `partial`. `README.md` now documents these semantics. Existing zero classification remains for otherwise healthy empty results; unknown coverage alone remains insufficient to classify a source as partial.

Offline checker tests cover cap reached even with a crossed boundary, uncapped short history, partial zero, complete and unknown coverage, unavailable results, existing ordering and safe errors. Against the original checker, **five cases failed and six passed**, detecting four incorrect coverage labels and the returned-unavailable/zero mismatch. Restored the fix afterward. No publisher requests are needed for these regressions.

## SPECTRA-201 (resolution links) evidence

The collection returned **two ordinary bills and zero resolutions**:

| Measure | Action date | Built public link | Public-page HTTP status |
|---|---|---|---|
| Senate bill 3315, Health Care Cybersecurity and Resiliency Act of 2026 | 2026-10-05 | https://www.congress.gov/bill/119th-congress/senate-bill/3315 | Not requested: ordinary bill |
| House bill 10238, Cybersecurity for Small Businesses Act of 2026 | 2026-10-13 | https://www.congress.gov/bill/119th-congress/house-bill/10238 | Not requested: ordinary bill |

The packet's conditional request for two or three resolution-page probes had no eligible items. No public resolution page was requested and no Hypertext Transfer Protocol (HTTP) status is claimed. Did not substitute fixture resolutions or broaden the legislative search just to manufacture live evidence. SPECTRA-201 (resolution links) therefore has **no new live resolution-link verification** from this rehearsal.

## Remaining surprises for November 1 at 05:00

- Five feeds still have partial monthly history. Counts and successful transport do not close the completeness concern; retain the warnings when selecting and describing report coverage.
- FedRAMP notices still yields zero. Keep its warning visible; no parser defect or publisher silence was proven here.
- Congress.gov worked with this run's credential access. The scheduler's own unattended credential access was not exercised; a missing key must yield unavailable/unknown, never verified zero.
- Three API/catalog fetchers report unknown coverage. The new metadata distinguishes unknown from false; it is not a universal archive-completeness certificate.
- Remaining month-end publications can change counts, page needs and remote availability. Neither recovered feed reached its cap in this snapshot, but bounded caps still apply on November 1.
- The source checker intentionally exits successfully for partial coverage, as before for successful fetches. Automation must read the statuses/warnings, rather than infer completeness from process success or the aggregate succeeded count.

## Validation and dispatcher facts

After cleanup, the required report existence check and full suite passed: **163 tests in 0.25 seconds**. `git diff --check` also passed. No ambient temporary-directory Git issue occurred. The sole temporary collection directory and all raw/prepared/measurement files were deleted after extracting this report; no source artifacts are retained in this worktree.

```text
test -s docs/plans/2026-10-29-november-final-rehearsal.md && python -m pytest -q
```

Only the checker, README, two offline test files and this report changed. No Git mutations, tracker edits, source configuration changes, scheduler changes, publication or delivery occurred. The dispatcher owns integration and tracking. The combined health/history path is rehearsed successfully; do not close the overall monthly coverage concern or SPECTRA-201 (resolution links) on this evidence. No new ticket identifiers were allocated.

For Jeff: acceptance of limited coverage for the five rolling feeds or a change to cadence/archive strategy remains a product decision. This packet makes neither decision.
