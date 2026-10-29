# API fetcher coverage — October 29, 2026

Coverage metadata now describes the three application programming interface (API) fetchers without changing their requests, item construction, filtering, retries, authentication, or exit behavior. The November issue uses `2026-10-01 <= date < 2026-11-01`.

## Field derivation

| Source | `pages_fetched` | `page_cap_reached` | `window_start_reached` |
|---|---|---|---|
| Federal Register | Count each successful parsed result page, including an empty terminal page. | True only when all ten iterations complete with a remaining `next_page_url`; false on exhaustion, including exhaustion exactly on page ten. | True: the existing publication-date query bounds the requested window on the server, including for an empty result. This does not override a cap warning. |
| Cybersecurity and Infrastructure Security Agency (CISA) Known Exploited Vulnerabilities (KEV) | One after the full catalog download parses. | False: no local result/page limit. | True: the full catalog is downloaded before the existing local date filtering. |
| Congress.gov | Count successful parsed bill pages before local relevance/action filtering and deduplication. | False on returned results; reaching the existing configured cap with a remaining next page still raises. | True if any returned bill has a valid action date strictly before the start, even if irrelevant or duplicated. Otherwise null: server bounds filter updates, not the action dates used for report items. Equality, invalid dates and empty results do not prove a crossed boundary. |

Missing Congress.gov credentials still return `unavailable` with all three coverage fields null. Exceptions still produce runner health `error` with null coverage; no partial item file is saved. No credentials, response headers, exception request details, or supplied Congress.gov continuation URLs were printed or retained.

## Scope decisions and offline evidence

The request for a capped result marked `partial` applies to Federal Register: its ten-page synthetic response retains exactly the same deduplicated item and health now reports `partial`. A catalog download has no capped-result path. Congress.gov already raises on its cap; changing that to a partial result would change returned items and error behavior, so the regression explicitly preserves `error`. Exposing coverage on exceptions would require a separate runner/error-contract change and is outside this packet.

`tests/collect/test_api_coverage.py` covers one/multiple Federal Register pages, exhaustion exactly at the cap, a remaining page at the cap, empty results, complete/empty KEV catalogs, Congress.gov pages/deduplication, older/equal/missing/invalid action dates, empty updates, unavailable credentials and the preserved cap error. Saved item dictionaries are checked in full, including identifiers, summaries, URLs and dates. Saved coverage/status must match `_health.json`.

The initial 12 new tests were run against the original three source modules: **11 failed, 1 passed**. Restoring the implementation made all 12 pass. Two further cases cover empty Federal Register results and unavailable Congress.gov coverage. The full suite passes **177 tests**. No ambient temporary-directory Git problem occurred.

## Live check

Ran October 29, 2026 at **06:47:37–06:48:29 Coordinated Universal Time (UTC)** (02:47–02:48 America/New_York), using the native repository's virtual environment and this worktree's `run_collect()` implementation. Loaded only these three sources from `src/collect/config.yaml` into a `tempfile.TemporaryDirectory(prefix="spectracov-")` outside the worktree and requested issue month `2026-11`. Each fetcher ran once; the selected source configurations have no core retry. Congress.gov's normal credential lookup succeeded and authentication remained solely in the `X-Api-Key` header. Logs and console output were suppressed during collection; only source names, statuses, counts and coverage fields were emitted afterward.

| Source | Status | Items | Pages | Cap reached | Window start reached |
|---|---|---:|---:|---|---|
| Federal Register | ok | 46 | 1 | false | true |
| CISA KEV | ok | 32 | 1 | false | true |
| Congress.gov | ok | 2 | 13 | false | true |

Congress.gov's true boundary means an older action was observed among the returned bills, not that the update query bounds action dates. Its 13 pages remain below the existing 40-page limit. The temporary configuration, source files and health report were deleted on context exit; the driver verified that the temporary folder no longer existed. No collected artifacts remain in the worktree.

## November 1 at 05:00 expectations

Federal Register now exposes a capped history as `partial`; CISA KEV reports complete catalog coverage. Congress.gov may legitimately retain an unknown action-date boundary after exhausting its update query. Its cap remains an error, and inaccessible credentials remain unavailable rather than a verified zero. These changes do not repair the five rolling feeds identified in `docs/plans/2026-10-29-november-final-rehearsal.md` or certify publisher completeness. Counts and remote availability may change before month end; this check does not exercise the unattended scheduler or its credential access.

Git integration and tracking remain with the dispatcher. No backlog, ticket status, source configuration, scheduler, publication, or delivery changes were made.
