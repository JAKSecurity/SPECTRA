# Open-ticket evidence — October 29, 2026

The eight written acceptance boxes have supporting evidence and can be checked, with the qualifications below. Tickets 001 (Congress zero items) and 002 (OpenAI zero items) are already Delivered; their unchecked boxes are stale. Ticket 201 (resolution links) meets its written mapping-and-test criterion, but its resolution notes impose an additional successful live-page verification gate. Keep that ticket Open until that gate is verified. No tracker changes are applied here.

## Evidence boundaries

This is an offline review of committed reports, current code and tests, and retained source-health files read from the designated native repository. No network, collection, scheduler, publication or delivery action occurred. Paths below are relative to that repository; retained ignored outputs are not present in this worktree.

The reports do not establish unattended scheduler success. The relevant collection snapshots are:

| Evidence | Collection result | Congress.gov | OpenAI blog |
|---|---|---|---|
| `docs/plans/2026-10-28-november-collect-rehearsal.md`, “Method and timing” / “Source comparison” | October 29 at 00:14–00:15 Coordinated Universal Time (UTC), October 28 locally; 362 items, 17 successful sources | `ok`, 2 | `ok`, 67 |
| `docs/plans/2026-10-29-november-final-rehearsal.md`, “Source comparison” | October 29 at 02:38–02:39 UTC; 394 items, 17 successful sources, five partial | `ok`, 2 | `ok`, 67 |
| `docs/plans/2026-10-29-api-fetcher-coverage.md`, “Live check” | October 29 at 06:47–06:48 UTC; three-source check, not a 17-source rehearsal | `ok`, 2; 13 pages, no cap, older action observed | Not collected |
| `docs/plans/2026-10-29-november-post-merge-check.md`, “Per-source comparison with the final rehearsal” / “Preparation and window-check results” | October 29 at 10:41–10:42 UTC; 397 items, 17 successful sources, five partial | `ok`, 2; 13 pages, no cap, older action observed | `ok`, 67; one page, no cap, window start crossed |

The three full collection snapshots are 362, 394 and 397 items, rather than three runs all in the 394–397 range. The first report's filename uses its local October 28 date. Each report records checking saved counts against `_health.json`; its temporary raw files and health report were subsequently removed. Thus these are committed run attestations, not independently re-read November health files. Aggregate success includes partial sources and does not certify complete monthly coverage.

Directly inspected retained health provides additional historical evidence. In `data/sources/2026-08/_health.json`, `data/sources/2026-09/_health.json` and `data/sources/2026-10/_health.json`, the `sources` entry for `openai_blog` is `status="ok"` with `items=42`, `56` and `72`, respectively. The corresponding Congress.gov counts are all zero. Those older Congress zeros do not contradict the later repair rehearsals, and are not positive closure evidence. No November output is retained in either inspected repository location.

## Ticket 001 (Congress zero items)

Source: `docs/tickets/001-congress-gov-zero-items.md`, “Acceptance Criteria”.

### Box 1 — met

> Root-cause why `congress_gov` returns 0 (run the collector in isolation; inspect the
> API request, key, query params, and raw response).

The ticket's “Diagnosis confirmed + wiring done (2026-06-03)” identifies absent credential injection/loading and the silent missing-key empty result. Its “Closed (2026-06-03)” records provisioning and a fetch of 20 measures through the production fetcher. This is historical documented diagnosis, not a newly repeated raw-response inspection. Current `src/collect/fetchers/congress_gov.py:46-87` implements configuration → environment → keyring lookup and explicitly returns `unavailable` when none is readable. `tests/collect/test_congress_gov.py::TestCongressGovFetcher::test_returns_unavailable_without_api_key` verifies that distinction offline.

The original missing-key diagnosis is supported. It should not be extended to assert that every later zero had the same cause; the retained August–October zeros predate the current successful rehearsals.

### Box 2 — met

> Fix so a normal month returns a non-trivial item count.

The final rehearsal's “SPECTRA-201 (resolution links) evidence” identifies two qualifying October measures: Senate bill 3315, Health Care Cybersecurity and Resiliency Act of 2026, and House bill 10238, Cybersecurity for Small Businesses Act of 2026. The post-merge comparison again records two items, with action dates October 5 and 13, after 13 pages and no cap. Current `src/collect/fetchers/congress_gov.py:93-173` exhausts the bounded update query and filters relevance and action dates locally. `tests/collect/test_source_regressions.py::test_congress_relevance_window_pagination_and_header` verifies paging, relevance, dates and header authentication.

Judgment: two actual relevant measures are non-trivial for the configured legislative scope; the box specifies no numerical minimum. The older unfiltered 20-item fetch is not today's count target. This establishes repaired collection in an ordinary monthly window, not a promise of positive legislative activity every month or proof of the upcoming unattended run.

### Box 3 — met

> Confirm a subsequent (or forced) run reports congress_gov with items > 0 in `_health.json`.

The final rehearsal's “Source comparison” / “Method and timing” and the post-merge report's “Preparation and window-check results” explicitly record reading `_health.json`, matching every source-file count to health, and Congress.gov returning two items. A forced run is expressly allowed by the box, so November 1 is not required to check it. The reports' removed temporary files limit independent replay of that historical evidence, not what the reports attest.

Superseded assumption: the June resolution's statement that a missing key preserves graceful-empty behavior no longer describes the code. Missing credentials now mean unavailable and an unknown health count, covered by `tests/collect/test_coverage_health.py::test_missing_congress_key_is_unavailable_end_to_end` and `tests/collect/test_api_coverage.py::test_congress_missing_key_keeps_coverage_unknown`. These tests were inspected; the post-merge report records the full 177-test suite passing. None of the three acceptance boxes is obsolete; the historical implementation description is.

## Ticket 002 (OpenAI zero items)

Source: `docs/tickets/002-openai-blog-zero-items.md`, “Acceptance Criteria”. OpenAI uses the generic Really Simple Syndication (RSS) fetcher in `src/collect/fetchers/rss.py`, not a dedicated OpenAI module.

### Box 1 — met

> Root-cause the June regression (run the collector in isolation; check the feed URL
> resolves and returns entries; inspect the raw response).

The ticket's “Resolution (2026-06-03)” records the old `/blog/rss.xml` address redirecting to `/news/rss.xml`, attributes the zero to redirect/transient handling, and records 989 entries through the production fetcher. `src/collect/config.yaml:53-59` preserves that diagnosis and canonical address. Treat this as the existing historical diagnosis: neither current tests nor October rehearsals can reconstruct the exact failed June response, and no retained June raw response was available for independent inspection. The later reports establish recovery, not new proof of the precise historical transport event.

### Box 2 — met

> Update the feed URL / parser as needed.

`src/collect/config.yaml:53-59` selects `https://openai.com/news/rss.xml`. `src/collect/fetchers/rss.py:33-41` fetches the response with `requests`, whose request follows redirects, then parses the response body. The post-merge report's “Per-source comparison with the final rehearsal” records 67 OpenAI items from this configured production path. This meets the requested repair; an OpenAI-specific parser is unnecessary.

### Box 3 — met

> Confirm a subsequent (or forced) run reports openai_blog with items > 0 in `_health.json`.

The directly inspected retained August, September and October health entries record 42, 56 and 72 items. The final rehearsal and post-merge report additionally attest matched health/source counts of 67 for the November issue's October window. These are subsequent/forced runs, exactly as permitted by the criterion; scheduler execution on November 1 is not a prerequisite.

### Box 4 — met

> Sanity-check the item count is reasonable for a blog feed (not the prior ~930).

The ticket's resolution explains the roughly 989-entry fetch as the full archive, not hundreds of new monthly publications. Current `src/collect/fetchers/rss.py:74-83` excludes undated and out-of-window entries when the report window is supplied. `tests/collect/test_rss.py::TestRSSFetcher::test_filters_to_explicit_content_window` verifies the inclusive start and exclusive end behavior. The post-merge report records 67 saved posts dated October 1–28, with the older-date boundary crossed and no page cap; retained earlier issue counts are 42, 56 and 72. That supports a plausible monthly count without treating it as a guarantee about publisher completeness or individual article quality.

Superseded assumption: “not the prior ~930” is no longer a useful limit on the upstream archive size. The acceptance intent remains valid for saved monthly items, and the box can be checked on that basis. The June claim that downstream curation would contain the archive is not needed to justify current collection counts. No box needs deletion or an obsolete checkbox state.

## Ticket 201 (resolution links)

Source: `docs/tickets/201-congress-resolution-links.md`, “Acceptance”.

### Box 1 — met as written; additional live gate not met

> Each measure type (HR, S, HRES, SRES, HCONRES, SCONRES, HJRES, SJRES)
> maps to its correct congress.gov path, with a test per type.

`src/collect/fetchers/congress_gov.py:15-43` implements the explicit mapping and uses it in `_bill_url`. `tests/collect/test_congress_gov.py::TestBillUrl::test_measure_type` has all eight parameterized cases:

| Measure type | Meaning | Expected path |
|---|---|---|
| HR | House bill | `house-bill` |
| S | Senate bill | `senate-bill` |
| HRES | House simple resolution | `house-resolution` |
| SRES | Senate simple resolution | `senate-resolution` |
| HCONRES | House concurrent resolution | `house-concurrent-resolution` |
| SCONRES | Senate concurrent resolution | `senate-concurrent-resolution` |
| HJRES | House joint resolution | `house-joint-resolution` |
| SJRES | Senate joint resolution | `senate-joint-resolution` |

All eight cases passed again in this offline review. The ticket's “URL evidence checked on 2026-10-26” records indexed Congress.gov content confirming those paths. It also records Hypertext Transfer Protocol (HTTP) 403 responses from direct fetches, and explicitly leaves successful live fetching unverified. The final rehearsal produced two ordinary bills and zero resolutions; its resolution-evidence section says no public resolution page was requested. The post-merge report adds no resolution-page verification. Unit tests and search-index observations cannot close that separate gate.

Recommendation: check the literal mapping/test box with a note preserving the live gate, but retain Open in the ticket and backlog. Do not rewrite the historical failed checks as successful. The extra gate is **not met**, rather than automatically “needs the 2026-11-01 run”: even that run may contain no resolutions and collection does not fetch their public reader pages. It requires a successful live check of identified resolution pages. No criterion here is obsolete.

## Follow-up after November 1 at 05:00 America/New_York

Unattended scheduler invocation, its credential access and final October counts **need the 2026-11-01 run**. They are separate operational checks, not extra conditions silently attached to the seven historical zero-item boxes. Wait for that run to finish; absence at exactly 05:00 alone is not a failure. Run these commands from the native repository root, not the disposable worktree. None was run during this packet.

First inspect the scheduled run's retained health without recollecting or overwriting evidence:

```bash
.venv/bin/python - <<'PYCODE'
import json
from pathlib import Path
p = Path('data/sources/2026-11/_health.json')
if not p.exists():
    raise SystemExit('November health not found; inspect scheduler completion before retrying.')
h = json.loads(p.read_text())
print('timestamp:', h.get('timestamp'))
print('report_month:', h.get('report_month'))
print('content_window:', h.get('content_window'))
for source in ('congress_gov', 'openai_blog'):
    entry = next((r for r in h.get('sources', []) if r.get('source') == source), None)
    print(source, {k: entry.get(k) for k in
          ('status', 'items', 'pages_fetched', 'page_cap_reached', 'window_start_reached')}
          if entry else 'missing health entry')
PYCODE
```

Confirm the issue is `2026-11`, the window is October 1 inclusive through November 1 exclusive, and the timestamp belongs to the completed scheduled run; correlate it with the automation's completion record. A manually created health file alone does not prove scheduler invocation. Missing Congress.gov credentials must show unavailable/unknown, not a verified zero. Do not require counts to equal the rehearsal snapshots.

For a fresh read-only source diagnostic, including both sources, run:

```bash
.venv/bin/python scripts/check-source-window.py --all --report-month 2026-11
```

This command makes live requests and prints safe counts/statuses; it does not save `_health.json` or prove unattended credential access. Its default without `--all` omits OpenAI, hence the explicit flag.

For the remaining ticket 201 (resolution links) live gate, probe the eight exact public pages already identified by the ticket; no application programming interface (API) credential is needed:

```bash
while IFS= read -r path; do
  curl --silent --show-error --location --fail --max-time 30 \
    --output /dev/null --write-out '%{http_code} %{url_effective}\n' \
    "https://www.congress.gov/bill/119th-congress/$path"
done <<'PAGES'
house-bill/6100/titles
senate-bill/391/all-info
house-resolution/201/text/ih
senate-resolution/7/all-actions
house-concurrent-resolution/16/text/ih
senate-concurrent-resolution/19/text/is?format=txt&overview=closed
house-joint-resolution/35/text/eh?format=txt
senate-joint-resolution/15/committees
PAGES
```

Record each status and effective address, then inspect each successful page in a browser to verify the measure type/number rather than a challenge or unrelated landing page. A blocked request or a misleading success response leaves the gate open. These are known historical pages, not a claim that November collection returned resolutions. If November contains resolutions, also verify their generated reader links. No paid service, delivery or source-scope change is proposed.

## Validation and judgment calls

- This run: 29 offline tests passed in 0.10 seconds: all of `tests/collect/test_congress_gov.py`, `tests/collect/test_rss.py::TestRSSFetcher::test_filters_to_explicit_content_window`, and `tests/collect/test_source_regressions.py::test_congress_relevance_window_pagination_and_header`. Used the native repository's virtual-environment interpreter against this worktree, with bytecode writing disabled and the pytest cache provider disabled. No network or temporary Git repositories were needed; no ambient temporary-directory Git issue occurred.
- The post-merge full-suite result of 177 passing tests is cited historical evidence, not a full-suite rerun here. This report adds no code and therefore adds no regression test.
- Accepted committed diagnosis/run attestations where raw historical responses or temporary rehearsal files are absent, with those limits stated explicitly.
- Interpreted two qualifying legislative measures as non-trivial and the OpenAI count criterion as a monthly-output sanity check.
- Separated the literal resolution mapping/test box from its documented additional live gate; checking that box does not authorize ticket closure.
- Required completion check: `test -s docs/plans/2026-10-29-open-ticket-evidence.md && git diff --check`.

## Exact tracker edits proposed for the interactive session

Box numbers below follow their order in the ticket and correspond to the complete quotes above. These are proposals only; no tracker, status, priority, capability or project field was edited.

| Ticket file | Box | New state | Evidence to append with the change |
|---|---|---|---|
| `docs/tickets/001-congress-gov-zero-items.md` | 1: Root-cause | `[x]` | Ticket's June 3 diagnosis/provisioning; current credential lookup and unavailable regression; this report, “Ticket 001 (Congress zero items)”, Box 1. |
| `docs/tickets/001-congress-gov-zero-items.md` | 2: Non-trivial count | `[x]` | Final rehearsal, resolution-evidence section: two named relevant bills; post-merge comparison: two items over 13 pages; this report, Box 2. |
| `docs/tickets/001-congress-gov-zero-items.md` | 3: Positive health count | `[x]` | Final rehearsal and post-merge saved-health/source count matching attestations: Congress.gov 2; this report, Box 3. |
| `docs/tickets/002-openai-blog-zero-items.md` | 1: June root cause | `[x]` | Existing June 3 resolution and canonical-address comment; historical raw-response limitation retained; this report, “Ticket 002 (OpenAI zero items)”, Box 1. |
| `docs/tickets/002-openai-blog-zero-items.md` | 2: Feed/parser update | `[x]` | `src/collect/config.yaml:53-59`, `src/collect/fetchers/rss.py:33-41`, and post-merge OpenAI 67; this report, Box 2. |
| `docs/tickets/002-openai-blog-zero-items.md` | 3: Positive health count | `[x]` | Retained August–October health counts 42/56/72 and post-merge matched health count 67; this report, Box 3. |
| `docs/tickets/002-openai-blog-zero-items.md` | 4: Reasonable count | `[x]` | Post-merge 67 October-dated posts, explicit-window regression, archive-versus-month distinction; this report, Box 4. |
| `docs/tickets/201-congress-resolution-links.md` | 1: Eight mappings/tests | `[x]`, with live gate note | `src/collect/fetchers/congress_gov.py:15-43`, all eight `TestBillUrl::test_measure_type` cases passing, ticket's indexed-page evidence; this report, “Ticket 201 (resolution links)”. Append: “Mapping/test criterion met offline; successful live reader-page verification remains unverified. Ticket remains Open.” |

Retain Delivered for tickets 001 (Congress zero items) and 002 (OpenAI zero items), in both their status lines and `docs/BACKLOG.md:18-19`. Retain Open for ticket 201 (resolution links), in its status line and `docs/BACKLOG.md:22`; no status transition or new resolved date is supported yet. If updating `docs/BACKLOG.md:25` for clarity, replace only `Open: 201 (resolution links).` with `Open: 201 (resolution links; mapping/tests verified, successful live reader-page verification pending).` No `projects.yaml` edit or new ticket is proposed. After successful live-page verification, an interactive session can attach the dated page evidence and separately propose closure; the November scheduler run alone does not supply it.
