# Options for five short-history feeds

**Decision (Jeff, 2026-10-30):** option 3 for the November 2026 issue: keep sources and cadence as they are, and state the partial coverage plainly in the issue (`AGENTS.md`, Source coverage note). Source and cadence changes stay open.

**Recommendation for Jeff's decision:** retain CISA, Nextgov and Dark Reading
with more frequent collection; replace The Record with Krebs on Security if
less frequent investigative coverage is acceptable; drop The Verge feed and
retain the already configured MIT Technology Review feed. Keep the report
monthly. These are proposals, not approved source or scheduling changes.

Checked October 29, 2026, 02:43–02:45 Coordinated Universal Time (UTC), still
October 28 in America/New_York. The November issue's content window is
`2026-10-01 <= published < 2026-11-01`. October is not yet complete.
Really Simple Syndication (RSS) and Atom feeds below are rolling snapshots.
Reaching September establishes available history across the month boundary,
not that a publisher exposes every article.

| Source | Current snapshot and prior report contribution | Replacement option | Weekly / accept partial / drop options | Recommendation |
|---|---|---|---|---|
| Cybersecurity and Infrastructure Security Agency (CISA) advisories | 30 entries, October 20–28; **3** directly attributed report items, excluding the separate vulnerability catalog. | Official alerts-only RSS reaches September 14: **16 October alerts**, readable by `rss`, but omits advisory/resource categories. Official machine-readable advisory indexes reach 2010/2024; they and the public advisory listing offer archive routes requiring new code and scope reconciliation. The catalog already collected is not an advisory replacement. See CISA evidence below. | **Weekly:** plausible at recent volume, little burst margin; not proven for all October. **Partial:** knowingly lose earlier advisories. **Drop:** lose an authoritative source; other reporting is not equivalent. | **Keep scope; propose twice-weekly capture**, with gap detection. Prefer an archive implementation if monthly-only collection is mandatory. Do not silently substitute alerts-only coverage. |
| Nextgov cybersecurity | 25 entries, October 6–29 UTC; **17** prior report items. | Public category archive yields **28 unique October article links**, reaches October 1 and September; requires a new page parser. Publisher-wide RSS has only 21 entries, October 23–29, so is worse. CyberScoop already supplies related federal coverage with verified history, but is not a second independent replacement. | **Weekly:** likely adequate at observed rate and feed size. **Partial:** at least three October archive articles are outside the current feed. **Drop:** largest measured editorial loss among these five. | **Keep; collect weekly.** If monthly-only is required, prioritize the category archive over replacing this publisher. |
| Dark Reading | 50 entries, October 15–28; **5** prior report items. | Publisher-advertised sitemap/archive endpoints return 403 with the production identity. Krebs on Security spans the month and uses `rss`, but supplies narrower investigations rather than equivalent security-industry breadth. | **Weekly:** likely adequate at observed rate, with useful margin. **Partial:** earlier October remains unobserved. **Drop:** lose incident and artificial intelligence (AI) security analysis used in both recent issues. | **Keep; collect weekly.** No verified monthly, like-for-like replacement in this investigation. |
| The Record | 5 entries, all October 28 within 4 hours 13 minutes; **2** prior report items. | **Krebs on Security:** 10 entries, September 8–October 21, including **6 October items**; existing `rss` reads them and crosses the boundary. Less frequent cybercrime/investigative coverage, with less daily international and policy breadth. The Record's advertised alternate feed is only a redirect to the same five entries. | **Weekly:** inadequate at a sustained five-per-publishing-day rate. **Partial:** monthly collection samples approximately one recent day's output. **Drop:** loses a distinct reporting voice; recent zero selection does not prove low value. | **Replace with Krebs**, subject to accepting narrower coverage. If The Record's voice is essential, investigate several captures per day plus overlap monitoring; weekly is not the repair. |
| The Verge AI | 10 entries, October 27–28; **0** prior report items. | Publisher's October sitemap contains **1,284 site-wide URLs**, with dated early-month evidence, but needs article-date/category parsing. Existing **Massachusetts Institute of Technology (MIT) Technology Review AI** paging yields **27 October items**, October 2–28, then September; no additional source is needed. | **Weekly:** inadequate; nine of ten entries were published on October 28. **Partial:** accept a one-to-two-day sample. **Drop:** no measured loss in the three reports, but less consumer/product and broad technology reporting. | **Drop this feed; retain MIT Technology Review** for independent AI journalism. A sitemap integration is available if Verge-specific breadth is worth maintaining. |

## Two-minute decision

1. **Recommended mix:** keep the three sources that supplied most selected
   items; capture CISA twice weekly and Nextgov/Dark Reading weekly. Replace
   The Record with Krebs and drop The Verge feed. A common twice-weekly
   capture for all three retained feeds would simplify scheduling. Monthly
   curation, human review and delivery remain monthly.
2. **If collection must remain once a month:** prioritize Nextgov's public
   archive and a CISA archive integration. Keep Dark Reading explicitly
   partial until an accessible archive is established. Use Krebs and the
   existing MIT Technology Review feed for the two very short feeds. The
   archive work is new implementation, not a ready configuration switch.
3. **Lowest implementation effort:** keep everything monthly and explicitly
   accept partial source coverage. This preserves some recent articles,
   but does not support a claim of complete monthly coverage. Dropping all
   five would discard publishers responsible for 27 selected items across
   the three available reports; it is not justified by feed transport alone.

Starting frequent collection now cannot recover already expired October
entries. For November 1, either accept and disclose the remaining gaps or
separately authorize archive/manual supplementation. No source replacement,
cadence change, archive implementation, publication or delivery occurred here.

## Evidence and compatibility

The fetcher registry in `src/collect/fetchers/__init__.py` has four types:
`rss`, `federal_register`, `cisa_kev`, and `congress_gov`. Only `rss` is a
general feed reader; its paging implementation uses WordPress `paged`.
The three specialized fetchers have fixed service-specific formats/endpoints.
There is **no generic sitemap, web-page archive, or arbitrary JavaScript
Object Notation (JSON) fetcher**. An XML sitemap is not an RSS feed.

### CISA: useful official history, but multiple scopes

- [Configured combined feed](https://www.cisa.gov/cybersecurity-advisories/all.xml):
  200, 30 unique identities, October 20–28. Twenty entries share October 22;
  batch publication matters more than a simple monthly average.
- [Alerts-only feed](https://www.cisa.gov/cybersecurity-advisories/alerts.xml):
  200, 30 entries, September 14–October 28; 16 in October, starting October 1.
  Replaying the captured response through `RSSFetcher` returns those 16 and
  `window_start_reached=True`. This is a working configuration-only candidate
  **for a narrower alerts scope**, not a replacement for combined advisories.
- [Public advisory listing](https://www.cisa.gov/news-events/cybersecurity-advisories),
  its advertised [page 2](https://www.cisa.gov/news-events/cybersecurity-advisories?page=1)
  and [page 3](https://www.cisa.gov/news-events/cybersecurity-advisories?page=2):
  all 200, ten dated cards each. The first two pages contain 20 October
  cards; the third contains October 1 followed by September 30–22. The
  **21 October cards** comprise 16 alerts, two cybersecurity advisories and
  three resources. No industrial-control advisory cards appeared in these
  pages, although those occur in the combined feed. This archive crosses the
  boundary for its listing scope, not the entire combined-feed scope.
  Titles, links and dates are available; summaries would require article
  retrieval or a deliberate metadata-only collection design.
- The [official CISA advisory repository](https://github.com/cisagov/CSAF)
  links [provider metadata](https://www.cisa.gov/sites/default/files/csaf/provider-metadata.json),
  which advertises Common Security Advisory Framework (CSAF) indexes.
  Both fetched indexes returned 200. The
  [operational technology index](https://raw.githubusercontent.com/cisagov/CSAF/develop/csaf_files/OT/white/cisa-csaf-ot-feed-tlp-white.json)
  has **3,991 unique advisory identities**, publication dates February 27,
  2010–October 27, 2026; **41 first published in October**, October 1–27.
  The [information technology index](https://raw.githubusercontent.com/cisagov/CSAF/develop/csaf_files/IT/white/cisa-csaf-it-feed-tlp-white.json)
  has **103 unique identities**, July 19, 2024–October 22, 2026; **9 first
  published in October**, October 1–22. These are JSON indexes with titles,
  identifiers, publication/update timestamps and links to individual JSON
  advisories, not directly usable RSS. The operational index has **53 October
  updates**, distinct from 41 initial publications. Preserve that distinction
  in any integration. The advertised third, vendor-advisory distribution was
  not fetched within the request budget. Index counts do not prove parity
  with `all.xml`; individual advisory content was not downloaded.
- [Known Exploited Vulnerabilities (KEV) catalog](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json):
  200, **1,762 entries**, addition dates November 3, 2021–October 28, 2026;
  **32 October additions**. Existing `cisa_kev` can read it and is already
  enabled. It supplies vulnerability/prioritization records, not policy
  guidance or full advisories; substituting it would remove information and
  duplicate an existing source.

### Nextgov: a usable public archive, no better alternate feed

The [category page](https://www.nextgov.com/cybersecurity/) advertises
[older results](https://www.nextgov.com/cybersecurity/more/?page=2).
Those results advertise [the next page](https://www.nextgov.com/cybersecurity/more/?page=3).
All three return 200. The category page has 21 unique article links dated
October 9–29; the second has 20 articles, October 9–September 11, including
eight October articles. Deduplicating their shared article yields **28 October
links**, including October 1 and 5 and a second October 6 article absent from
the current 25-entry feed. The third page is entirely older, September
10–August 10. Dates come from article-card `time` elements, not the page's
own generation timestamp. Repeated featured cards and referral query strings
must not create duplicate items.

The [About page](https://www.nextgov.com/about/) and category page link the
[all-content feed](https://www.nextgov.com/rss/all/): 200, 21 entries,
October 23–29. It parses as RSS but shortens history and adds unrelated
topics. The [robots file](https://www.nextgov.com/robots.txt) advertises no
sitemap. A category archive parser would preserve this publisher and current
topic better than switching feeds. CyberScoop's existing full-month path is
documented in `docs/plans/2026-10-28-feed-history.md`; it was not fetched
again here and does not preserve Nextgov's independent reporting.

### Dark Reading and The Record: limited same-publisher recovery

Dark Reading's [robots file](https://www.darkreading.com/robots.txt) advertises
the [sitemap](https://www.darkreading.com/sitemap.xml),
[news archive index](https://www.darkreading.com/news-archive-index.xml), and
[articles archive index](https://www.darkreading.com/articles-archive-index.xml).
All three returned **403**, as did the [homepage](https://www.darkreading.com/).
The [configured feed](https://www.darkreading.com/rss.xml) returned 200 and
50 entries. No date range can be claimed for the inaccessible archives.
No authentication or challenge bypass was attempted. The prior history
report's failed feed-self-link check was not repeated.

The Record's [homepage](https://therecord.media/) and
[news listing](https://therecord.media/news) returned 200. They did not expose
a usable older-results link or alternate history feed in the returned HTML.
The news listing is a client-rendered discovery lead, not verified month-long
article history. Its [robots file](https://therecord.media/robots.txt) returned
404. The advertised [slash-ending feed](https://therecord.media/feed/)
redirected to the [configured feed](https://therecord.media/feed), with the
same five identities. No guessed page parameters, sitemap filenames, or
private content-service endpoints were tried. These are bounded negative
findings, not proof that the publisher has no archive.

The alternative [Krebs on Security feed](https://krebsonsecurity.com/feed/)
returned 200 with ten distinct entries dated September 8–October 21,
including six in October, October 7–21. Captured-response replay through the
existing `rss` fetcher returned all six and crossed the October boundary.
The sampled October titles concern cybercrime investigations, ransomware,
sanctions and patching. This is a practical monthly replacement candidate
for The Record's incident/investigation role, and a narrower alternative for
Dark Reading; it is not an article-for-article substitute. Recheck retention
at month close because this remains a ten-entry rolling feed.

### The Verge: month archive exists; publication dates need care

The [robots file](https://www.theverge.com/robots.txt) advertises the
[sitemap index](https://www.theverge.com/sitemaps), which directly links
the [October sitemap](https://www.theverge.com/sitemaps/entries/2026/10).
All return 200. The October sitemap contains **1,284 unique article URLs**
with `lastmod` values October 1–28, including **170 URLs with the
`/ai-artificial-intelligence/` path**. This subset is not an AI-topic count:
AI stories also use `/tech/`, `/science/`, and other paths.

Two linked public pages were sampled: an
[October 1 article](https://www.theverge.com/ai-artificial-intelligence/1003197/amodeis-extreme-ai-warnings-were-questioned-by-tech-ceos)
and an [October 28 article](https://www.theverge.com/ai-artificial-intelligence/1021644/adam-mosseri-instagram-ai-negativity).
Both returned 200; their `article:published_time` values confirm those dates.
The two samples do not validate publication dates for all 1,284 URLs.
A sitemap integration needs original publication dates, topic classification,
canonical identities and public metadata/summary extraction. `lastmod` alone
must not move an old article into the current issue. No subscriber access was
used. The pages also advertise the
[site-wide Atom feed](https://www.theverge.com/rss/index.xml): 200, ten
entries dated October 28–29, an even shorter window than the AI feed.

The already configured
[MIT Technology Review AI feed](https://www.technologyreview.com/topic/artificial-intelligence/feed)
and its previously verified `?paged=2`, `?paged=3`, `?paged=4` URLs all
returned 200 with ten entries each. October counts are **10, 10, 7, 0**;
the union contains **27 identities**, October 2–28. Page 3 reaches September
30 and page 4 is entirely September. Replaying all four through the existing
fetcher with the configured six-page limit confirms 27 items, boundary
reached, and no exhausted cap. This covers the independent AI-journalism
role with available month history, not all of The Verge's product coverage.

## Would weekly collection have captured all October?

**No historical replay can establish that from one current feed snapshot.**
The estimates below assume a chronological feed with stable capacity and
successful captures no more than seven days apart throughout October. For
a feed retaining `N` entries, every inter-capture interval must contain at
most `N` new entries; spare capacity is needed to demonstrate overlap.
October 29–31 publications and earlier October bursts are not observed.

Rates use entry count divided by inclusive UTC calendar dates represented,
not the short intraday span between first and last entries. They are rough
planning rates, not measured full-month averages. The seven-day maxima are
counts in the retained sample, not maxima for all October.

| Source | Capacity / observed calendar days | Rough rate and weekly load | Weekly assessment |
|---|---|---|---|
| CISA combined | 30 / 9 | 3.3/day, about 23/week; observed seven-day maximum 27, with a 20-entry day | **Plausible, fragile.** Only three entries of margin over the observed seven-day load. Twice weekly gives more margin, but still needs overlap monitoring. |
| Nextgov | 25 / 24 | 1.0/day, about 7/week; observed seven-day maximum 11 | **Likely adequate**, assuming similar rates earlier in October. The dated archive strengthens the history option; it does not recreate earlier feed membership. |
| Dark Reading | 50 / 14 | 3.6/day, about 25/week; observed seven-day maximum 32 | **Likely adequate**, with 18 slots beyond the observed seven-day load. Early-month bursts remain unverified. |
| The Record | 5 / 1 | At least five on the sampled day; roughly 25–35/week if five recur on publishing days | **Not adequate at that sustained rate.** The sample cannot establish a long-term rate or a safe daily interval. |
| The Verge AI | 10 / 2 | 5/day, about 35/week; nine on October 28 alone | **Not adequate at that sustained rate.** Even daily could lose items during bursts; weekly does not address this feed's capacity. |

Frequent collection requires retention/health work as well as a schedule.
`src/curate/curate.py` already loads all saved source snapshots and removes
repeated identities at the same URL. That existing preparation can be reused;
it is not a missing pipeline. It does not merge a stable identity whose URL
changes between snapshots, and it keeps the first version of a repeated item.
An implementation should address those cases and define update handling:

- Preserve captures and merge by `(source, item identity)`, not by title or
  fetch date. `src/collect/fetchers/rss.py` hashes the publisher identifier,
  falling back to the reader URL; preserve the existing identity rules.
- Set the issue window explicitly. `src/collect/runner.py` normally selects
  the **previous calendar month**. An October capture intended for the
  November issue needs `--report-month 2026-11`; merely running the default
  command weekly in October would filter for September.
- `BaseFetcher.save()` uses a per-source, per-day filename. Weekly snapshots
  on different days can coexist, but multiple same-day captures overwrite
  one another. A higher-frequency strategy must retain or merge them before
  that overwrite. Handle month-end and interrupted runs explicitly.
- Track successful intervals and identity overlap; alert when an entire
  retained feed has rolled over between captures. An accumulated month's
  completeness cannot be inferred just from one feed's oldest date.

The current `src/collect/runner.py` already emits `partial` for short RSS
windows and `unavailable` for missing legislative credentials. Those fixes
postdate the rehearsal's findings; this packet does not propose reopening
them. They report gaps but do not restore missing history or implement
multi-capture retention.

## What dropping sources would cost in prior reports

Read all three available PDFs in the native repository's `output/` without
modifying them. These ignored files are absent from this worktree. Counted
source-attribution lines attached to substantive entries, once per entry;
excluded executive-summary repeats, prose mentions and conferences. Normalized
publisher names and source keys (for example `nextgov` and `Nextgov/FCW`).
The numbers measure **published editorial attribution, not proven automated
feed provenance or unique information unavailable elsewhere**. For example,
August's Nextgov article is in its acquisition category; October's CISA
resource is outside the alerts URL family. PDF attribution cannot show whether
those items arrived through a feed or manual supplementation.

| Publisher/source role | `output/2026-08-SPECTRA.pdf` (July content) | `output/2026-09-SPECTRA.pdf` (August content) | `output/2026-10-SPECTRA.pdf` (September content) | Total |
|---|---:|---:|---:|---:|
| CISA directly attributed guidance/alerts; excludes KEV | 0 | 1 | 2 | **3** |
| Nextgov | 1 | 10 | 6 | **17** |
| Dark Reading | 0 | 2 | 3 | **5** |
| The Record | 2 | 0 | 0 | **2** |
| The Verge | 0 | 0 | 0 | **0** |
| Total for the five | 3 | 13 | 11 | **27** |

Audit locations: August Nextgov page 1, The Record page 4; September CISA
page 3, Nextgov pages 2/4/5/7 (3/4/2/1 items), Dark Reading pages 3/5;
October CISA page 3, Nextgov pages 2/4/5/6 (3/1/1/1), Dark Reading page 5.
Separately, KEV supplied **0/5/5** entries across these issues and remains
enabled under every proposal above. CISA material attributed to other
publishers is not counted as CISA-source contribution. The two Record
selections concern Iran-linked operational-technology attacks and Russian
webmail espionage. Zero Verge selections may reflect collection gaps,
editorial selection or topic overlap; it is not proof of no useful output.

## Request budget, validation and dispatcher facts

Direct probes used Python `requests.get`, a 30-second timeout, redirect
following and the production identity from `src/collect/fetchers/rss.py`:
`SPECTRA-monthly-report/1.0 (+https://github.com/JAKSecurity/SPECTRA)`.
Only public pages/feeds were fetched; no credentials, sessions, private
application endpoints or subscriber feeds were used. Pagination links were
read from returned pages; the MIT feed parameters were already verified in
`docs/plans/2026-10-28-feed-history.md`. Search-engine discovery was separate
from these direct measurements and does not establish production access.

| Publisher | Direct requested URLs | Outcome / budget notes |
|---|---:|---|
| CISA, including official GitHub/raw advisory indexes | 10 | Combined feed, alerts feed, listing and two linked pages, KEV, repository, provider metadata, two advertised JSON indexes; all 200. |
| Nextgov | 7 | Cybersecurity feed, robots, category page, About, all-content feed, two linked archive pages; all 200. |
| Dark Reading | 6 | Feed and robots 200; three advertised archive/sitemap endpoints and homepage 403. |
| The Record | 5 | Feed, robots, homepage, news listing, advertised feed alias; robots 404, other final responses 200. Alias adds one redirect request. |
| The Verge | 7 | AI feed, robots, sitemap index, October sitemap, two linked articles, site-wide feed; all 200. |
| Shared replacement checks | 5 | Krebs feed once; MIT feed plus three previously verified pages; all 200. |

Total: **40 direct URL probes, 41 HTTP requests including the one redirect**.
Temporary public responses supported counting and local parser replay; they
are not production collection data and were removed after extracting evidence.
No extra network calls were needed for parser replay. No new test is needed
for this documentation-only investigation; no bug fix is included.

Dispatcher: the five-feed product decision remains open. Record the archive
candidates, compatibility limits, contribution counts and weekly estimates;
do not mark monthly completeness resolved or apply source/cadence changes
without Jeff's decision. No tracking files, source/configuration files,
`data/` or `output/` were edited; no Git mutation was performed. The packet's
existence check and full test suite are the final acceptance checks.

Validation: `test -s docs/plans/2026-10-29-short-feed-options.md` passed;
the native virtual-environment interpreter running `python -m pytest -q`
reported **154 passed in 0.29 seconds**. No ambient temporary-directory Git
interference occurred. Captured-response compatibility checks also passed for
the alerts-only, Krebs and four-page MIT candidates without network replay.
