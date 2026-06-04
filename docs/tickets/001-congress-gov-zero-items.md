# 001: congress_gov source returns 0 items (chronic since first run)
**Status**: Delivered  **Priority**: P2  **Type**: Bug
**Created**: 2026-06-03  **Resolved**: 2026-06-03

## Summary
The `congress_gov` source (Congress.gov API fetcher for cybersecurity bills) has returned
**0 items on every monthly run on record** — 2026-04, 2026-05, and 2026-06 all show 0. The
source-health monitor correctly flags it ("congress_gov: returned 0 items (feed may be stale
or broken)") but the warning has been re-reported monthly with no diagnosis or fix.

## Context
SPECTRA is `status: archived` (project complete) but the monthly pipeline runs unattended, so
this is a live maintenance bug. Detection works — what's missing is the closed loop that turns
a persistent warning into tracked work. That gap is being addressed separately in AI Assistant
ticket AIA-089 (auto-escalate persistent automation-health warnings into tickets).

Evidence (`data/sources/<YYYY-MM>/_health.json`):
- 2026-04: congress_gov = 0 items
- 2026-05: congress_gov = 0 items
- 2026-06: congress_gov = 0 items

Because it has been 0 since the very first run, this is most likely a **never-worked**
condition (mis-configured API query, missing/invalid `CONGRESS_GOV` API key, or an endpoint /
parameter that returns an empty result set), not a regression. Phase 2 marked the fetcher
"[x] complete" based on the collector running without error — but running without error is not
the same as returning items.

## Acceptance Criteria
- [ ] Root-cause why `congress_gov` returns 0 (run the collector in isolation; inspect the
      API request, key, query params, and raw response).
- [ ] Fix so a normal month returns a non-trivial item count.
- [ ] Confirm a subsequent (or forced) run reports congress_gov with items > 0 in `_health.json`.

## Diagnosis confirmed + wiring done (2026-06-03)
Root cause verified: `CONGRESS_GOV_API_KEY` is referenced **only** in the fetcher. SPECTRA has
no `.env`, no keyring loader, and the `spectra-monthly` scheduled task does not inject it -- so
the fetcher always hit the silent `if not api_key: return empty` path. 0 items since inception,
confirmed never-worked (not a regression).

Decision (Jeff, 2026-06-03): get a key and wire it (vs. disabling the source).

Code wired this session (`src/collect/fetchers/congress_gov.py`): api-key resolution is now
`config.api_key` -> env `CONGRESS_GOV_API_KEY` -> `keyring.get_password("ai-assistant",
"CONGRESS_GOV_API_KEY")` (the shared vault namespace used by scripts/secret_store.py), with a
safe `_keyring_api_key()` helper that returns "" on any
failure (preserves graceful-empty behavior when no key). `keyring>=24.0` added to
requirements.txt. Verified: no-key path still returns empty without crashing; full suite green
(59 passed). The fetcher will return bills as soon as the key is stored -- no further code
change needed.

### Closed (2026-06-03)
Key provisioned to keyring (`ai-assistant` / `CONGRESS_GOV_API_KEY`) and **verified**: the
congress_gov fetcher returned 20 bills (HRES 1025, HR 3033, S 2975, S 1199, ...) through
SPECTRA's own code path. Full suite green (60 passed).

**Secret-leak hardening (done same session):** while verifying, the key leaked into the run
transcript because the fetcher passed `api_key` as a URL query param and `requests` embeds the
full URL in `ConnectionError`/`HTTPError` messages. Fixes:
- Key now sent as an `X-Api-Key` **header**, never in the URL -> no URL-based error leaks it.
- Replaced `resp.raise_for_status()` with a scrubbed `RuntimeError(f"... HTTP {code}")`.
- New regression test `test_error_response_does_not_leak_api_key` asserts the secret is absent
  from any raised error.

**Provisioning note:** `getpass` paste was unreliable in the terminal (stored the key doubled,
then truncated to 1 char). Reliable method that worked: paste into a temp file, read+strip into
keyring, print length only, delete the file. The leaked key value should be regenerated if not
already (low severity -- read-only public-data key, rate-limit only).

## References
- Source collector: `src/` Congress.gov fetcher (`congress_gov`)
- Design: `docs/superpowers/specs/2026-04-10-spectra-design.md` (Congress.gov API source)
- Health reports: `data/sources/<YYYY-MM>/_health.json`
- Related: AI Assistant AIA-089 (auto-escalation loop)
