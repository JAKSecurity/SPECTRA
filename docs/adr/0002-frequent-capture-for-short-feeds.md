# Frequent capture for short-history feeds

Date: 2026-10-31. Decided by Jeff.

## Context

Five news feeds keep too little history for a once-a-month collection to
reach the start of the month (`docs/plans/2026-10-29-short-feed-options.md`).
For the 2026-11 issue Jeff chose to disclose the gap (AGENTS.md, Source
coverage note, 2026-10-30). This record settles the sources and cadence for
later issues.

## Decision

The options report's recommended mix:

- Capture `cisa_alerts` (the combined CISA advisories feed), `nextgov` and
  `dark_reading` between monthly runs. One shared twice-weekly schedule for
  all three, which the report notes is simpler than separate cadences and
  gives CISA the margin it needs.
- Replace `the_record` with Krebs on Security (`https://krebsonsecurity.com/feed/`).
  Its coverage is narrower; accepted.
- Drop `the_verge_ai`. MIT Technology Review AI already covers independent AI
  journalism with full-month history.
- Curation, human review and delivery stay monthly.

## Rejected

- Keep everything monthly and disclose partial coverage indefinitely: the
  lowest effort, but the issue could never claim full coverage of these
  publishers.
- Archive or sitemap integrations (Nextgov category pages, CISA CSAF indexes,
  The Verge sitemap): new parsers per publisher, and Dark Reading's archives
  return 403. Revisit only if frequent capture proves unreliable.
- Several captures a day to keep The Record: the report could not establish a
  safe interval from one sample.

## Consequences

Captures accumulate in the issue month's source folder and the monthly run's
preparation merges them. Source health must judge a captured source on all of
its captures (window start reached, no gap between consecutive captures), not
on the final fetch alone. The capture timer runs on the workstation, so a
powered-off week can still leave a gap; the gap check reports it.
