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

`fedramp-changelog.xml` reconstructs the four-entry response shape recorded in
`docs/reviews/2026-10-28-november-run-readiness.md`: shared reader link,
distinct feed identifier suffixes (98–95), titles, and October dates. The raw
response was unavailable; full identifier prefixes and publication times are
fixture values, not independently verified upstream fields. No live request
is needed to exercise collection and preparation.
