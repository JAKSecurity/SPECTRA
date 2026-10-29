# October feed history recovery

CyberScoop and MIT Technology Review now have verified feed history across
the October 1 boundary. Their October counts increase from **50 to 65** and
**10 to 27**, respectively. The other five feeds retain their existing
configuration: no supported public feed history path was established for them
within this bounded investigation. Complete monthly coverage remains unproven.

## Method

Checked October 28, 2026, America/New_York (October 29 Coordinated Universal
Time (UTC)); replay verification finished at 02:02 UTC. This is a snapshot
before the remaining month-end publications, not a November 1 collection.
The issue window was `2026-10-01 <= published < 2026-11-01`.

All direct publisher probes used Python `requests.get`, the exact production
User-Agent `SPECTRA-monthly-report/1.0 (+https://github.com/JAKSecurity/SPECTRA)`,
redirect following, and a 30-second timeout. Only public feed URLs were
requested; unsuccessful feed candidates sometimes returned an error page.
No credentials, cookies, subscriber feeds, article scraping, or private
application endpoints were used. Publisher/platform documentation searches
were separate discovery work, not count evidence or User-Agent verification.

The initial feed responses were captured once, and the complete captured
pages for the two successful sources were replayed through
`src/collect/fetchers/rss.py` to compare old and new configurations without
additional publisher requests. Counts below are unique production item
identities in the October window, not the number of XML elements or search
results. Unchanged feeds use their single live response for both columns.
CyberScoop's old baseline is its configured **five pages**, not one page.

## Results

| Source | Live October before → after | Earliest October after | Boundary evidence and disposition | Direct feed requests |
|---|---:|---|---|---:|
| Cybersecurity and Infrastructure Security Agency (CISA) advisories | 30 → 30 | October 20 | Rolling 30-item feed; no advertised continuation/archive link or documented history option found. Unchanged; October 1 not reached. | 1 |
| CyberScoop | 50 → 65 | October 1 | WordPress `?paged=N`; page 7 contains October 1 and September 30, page 8 is entirely September. Increase `max_pages` from 5 to 10. | 9 |
| Nextgov | 25 → 25 | October 6 | Rolling 25-item cybersecurity feed; only self and website links, no continuation/archive link. No documented older-feed method found. Unchanged; October 1 not reached. | 1 |
| Dark Reading | 50 → 50 | October 15 | Rolling 50-item feed. Its advertised self URL returns 404; no supported history option found. Unchanged; October 1 not reached. | 2 |
| The Record | 5 → 5 | October 28 | Five-item feed; no continuation/archive link, no WordPress generator, and no documented public history feed found. Unchanged; October 1 not reached. | 1 |
| The Verge artificial intelligence (AI) | 10 → 10 | October 27 | Atom feed; WordPress paging candidate and category-feed candidate both return 404. Unchanged; October 1 not reached. | 3 |
| MIT Technology Review AI | 10 → 27 | October 2 | WordPress `?paged=N`; page 3 contains October 2 and September 30, page 4 is entirely September. Enable paging with `max_pages: 6`. The archive crosses October 1 without an October 1 item. | 4 |

The successful sources add **32 unique October items** in this snapshot.
Their date crossing demonstrates available feed history through the start
of October; it does not certify that a publisher includes every article in
its feed. MIT Technology Review's earliest item being October 2 is not a
pagination failure: later pages already contain September publications.

## Verified paths and bounds

Both successful feeds explicitly identify WordPress in their generator field.
The [WordPress query documentation](https://developer.wordpress.org/reference/classes/wp_query/#pagination-parameters)
documents `paged`; it also explains that feed length is controlled by the
publisher's feed setting rather than a client's `posts_per_page` value.
No speculative feed-size parameters were sent.

- CyberScoop: `https://cyberscoop.com/feed/`, then the same URL with
  `?paged=2` through `?paged=8`. Every response was 200 and contained ten
  entries. October counts per page were **10, 10, 10, 10, 10, 10, 5, 0**;
  the identity union was 65. The first five pages yielded 50 and started
  October 8. The ninth request was an initial inspection of page 1 before
  the retained capture; it was not counted twice. The cap of 10 leaves two
  pages beyond the observed stopping page for month-end growth.
- MIT Technology Review:
  `https://www.technologyreview.com/topic/artificial-intelligence/feed`, then
  the same URL with `?paged=2` through `?paged=4`. Every response was 200
  with ten entries. October counts were **10, 10, 7, 0**; the identity union
  was 27. A cap of 6 leaves two pages beyond the observed stopping page.

The collector intentionally continues beyond a mixed October/September page
until **every dated entry on a page predates October 1**. This guards against
stopping before other October entries. Its existing ten-page clamp remains
unchanged: neither verified source requires a higher limit. Month-end volume
could still exhaust a cap; the existing page-cap warning remains relevant.

## Unrecovered sources and negative checks

These are bounded negative findings, not proof that no archive exists.

- CISA: `https://www.cisa.gov/cybersecurity-advisories/all.xml` returned
  200, 30 entries, October 20–28. The feed supplies no archive or next link.
  Documentation discovery did not establish a feed-specific history or size
  parameter. A narrower advisory category would change the source's scope
  and was not substituted. No guessed Drupal/WordPress parameters were sent.
- Nextgov: `https://www.nextgov.com/rss/cybersecurity/` returned 200,
  25 entries, October 6–28. The publisher's
  [About page](https://www.nextgov.com/about/) advertises Really Simple
  Syndication (RSS), but no historical feed option was identified. A digital
  magazine archive is not evidence of a cybersecurity feed archive. No
  guessed `page`, `paged`, or `limit` parameter was sent.
- Dark Reading: `https://www.darkreading.com/rss.xml` returned 200,
  50 entries, October 15–28. The response advertises
  `https://www.darkreading.com/feeds/rss.xml` as its self link; that exact
  URL returned 404. There is no next/archive link. The working configured
  URL was retained; an advertised self URL alone does not prove it works.
- The Record: `https://therecord.media/feed` returned 200, five entries
  dated October 28. Its generator names The Record, not WordPress; its
  channel contains no continuation/archive link. Its RSS specification link
  documents the format, not a publisher history parameter. No unsupported
  WordPress parameter was applied.
- The Verge: the configured
  `https://www.theverge.com/rss/ai-artificial-intelligence/index.xml`
  returned 200 with ten entries, October 27–28. WordPress asset URLs in that
  feed motivated a bounded platform check, but the same feed with `?paged=2`
  returned 404. Adding `/feed/` to the feed's linked category URL
  (`https://www.theverge.com/ai-artificial-intelligence/feed/`), following
  the [WordPress category-feed convention](https://developer.wordpress.org/advanced-administration/wordpress/feeds/),
  also returned 404 after redirecting to the slashless URL. Neither was
  configured. Its Atom self/alternate links advertise no older page. No
  subscriber-only feed was accessed.

## Fixtures and validation

`tests/collect/fixtures/cyberscoop-history-page-1.xml` through page 8 and
`tests/collect/fixtures/mit_tech_review_ai-history-page-1.xml` through page 4
retain two or three real items per captured response, with publisher
identifiers and dates intact. Content and unnecessary metadata were removed;
no tracking parameters, cookies or headers are retained. Fixture provenance
and the deliberately injected overlap are documented in
`tests/collect/fixtures/README.md`.

`tests/collect/test_source_regressions.py` verifies the approved paging
configuration, exercises the real trimmed shapes through HTTP response
replay, filters out September items, stops at the window boundary before
the configured margin, and deduplicates a repeated publisher identity whose
reader URL changes. Existing empty-feed, 404, cap-warning and undated-page
tests remain in place. Production parsing and paging logic did not change.

Full suite after configuration and fixture changes: **140 passed in 0.24
seconds**. All three configuration/history cases fail against the original
configuration, confirming they detect the missing recovery. Final acceptance
uses the packet's report existence check and the same full suite. No test
encountered the ambient temporary-directory Git
issue. No writes were made to `data/` or `output/`; temporary full responses
were kept only in the worktree and removed after extracting the fixtures and
measurements. No Git or tracker mutations were performed.

## Dispatcher and review facts

The feed-history portion of rehearsal item 2 is resolved for CyberScoop and
MIT Technology Review's available public feeds; it remains unresolved for
CISA advisories, Nextgov, Dark Reading, The Record and The Verge. Do not
close the overall monthly completeness concern or equate successful source
health with complete history. The rehearsal's structured completeness and
missing-credential health findings remain separate work.

For Jeff: the November 1 run has additional supported history, but acceptance
of limited coverage for the remaining five feeds or a change to collection
cadence/archive strategy still needs a product decision. No such decision,
scheduler change, publication or delivery was made here.
