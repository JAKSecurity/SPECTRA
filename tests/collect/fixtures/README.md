# Source regression fixtures

`cisa-alerts.xml` is the first item retained from the live CISA RSS 2.0 response
at https://www.cisa.gov/cybersecurity-advisories/all.xml on 2026-10-26.
`empty-feed.xml` and `unavailable.html` represent empty/transient responses;
no July response body or health file survives in the supplied source directory.

`congress-page-*.json` are small, deterministic API-shaped response fixtures,
based on the existing test payload and the Library of Congress bill endpoint
schema. Dates and titles deliberately exercise October boundaries; they are
not evidence of a live Congress.gov fetch. No key was readable in the sandbox.
The unrelated title reproduces the example in ticket 004 (Congress filtering).

`cyberscoop-history-page-*.xml` (pages 1–8) and
`mit_tech_review_ai-history-page-*.xml` (pages 1–4) retain two or three actual
items per live feed page checked October 28, 2026 local time (October 29 UTC),
using the production SPECTRA User-Agent. Page 1 uses the configured URL;
later pages append `?paged=N`. See `docs/plans/2026-10-28-feed-history.md`
for source URLs, counts, request budget, and coverage limitations.

These are trimmed response fixtures, not complete feeds: channel title, link,
description and generator, plus item title, link, GUID (globally unique
identifier), and publication date are retained; content, images, author data,
categories and other namespaces are removed. The boundary fixtures include
both October and September items; final pages contain only September items.
No dates or identities are invented. The `?p=` GUID values are publisher
identifiers, not tracking parameters. No cookies or response headers are saved.
The regression test deliberately copies an item onto the next page and changes
its reader URL to verify identity deduplication; that overlap is test-generated,
not claimed as an observed publisher duplicate.

`fedramp-changelog.xml` reconstructs the four-entry response shape recorded in
`docs/reviews/2026-10-28-november-run-readiness.md`: shared reader link,
distinct feed identifier suffixes (98–95), titles, and October dates. The raw
response was unavailable; full identifier prefixes and publication times are
fixture values, not independently verified upstream fields. No live request
is needed to exercise collection and preparation.
