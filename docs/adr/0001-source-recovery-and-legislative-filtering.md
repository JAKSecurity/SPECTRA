# Source recovery and legislative relevance

Date: 2026-10-26. Scope: 003 (CISA retry), 004 (Congress filtering).

## Decision

Core sources explicitly opt into one collector-level retry after one second
for exceptions or empty report-window results. Initially only CISA alerts is
marked core. RSS requests use HTTP status checking, redirects and a 30-second
timeout. Retain final empty/error health reporting rather than masking an outage
with stale prior-month data or retrying every source indefinitely.

Congress.gov `/bill` supports update-date filtering and pagination, but no
keyword search parameter. Apply configurable case-insensitive terms to title
and latest-action text and enforce latest-action dates locally. Keep the exact
previous calendar month when the runner supplies it; `days_back` is a fallback
for standalone fetches. Retain relevant resolutions. Fetch up to 40 pages of
250, exhaust the update window, and fail visibly if coverage exceeds the cap.
Do not stop pagination on an old action date: it is not an update timestamp.

## Alternatives and consequences

An undocumented `query`/`sort` request cannot guarantee relevance; a first-page
sample misses relevant bills beyond unrelated updates. Unbounded pagination
can stall unattended collection. The bounded local filter is reviewable and
requires no new service. It cannot find relevance appearing only in full bill
text or guarantee retrieval of actions whose records are updated after the
requested update window. Terms can be extended in source configuration.

Credentials stay in `X-Api-Key` headers, including paginated requests; never
follow response pagination URLs that might embed a key. Missing credentials
are reported as unverified by the read-only live checker. Offline fixtures
verify behavior but do not substitute for credentialed live validation.
