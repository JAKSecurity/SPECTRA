# 200: Restore SPECTRA after post-Claude automation cutover omission

**Status**: Delivered  **Priority**: P1  **Type**: Bug
**Created**: 2026-09-06

## Summary

SPECTRA did not move to an active scheduler when the workshop stopped using Claude Code in July 2026.  The July 1 issue was the last successful scheduled run.  No August or September invocation occurred, and no failure receipt was produced, because the replacement appliance cron inventory omitted SPECTRA entirely.

## Evidence

- The `ai-appliance` user crontab and user timers contain no SPECTRA job.
- The appliance has no SPECTRA checkout, report artifacts, or SPECTRA run log.
- Retained August 1 and September 1 briefing logs contain no 5:00 AM SPECTRA stage.
- The retired Claude task definition is a self-referential stub and cannot serve as a complete recovery runner.
- The project registry and repository documentation still claim that the monthly pipeline runs unattended.

## Acceptance Criteria

- [x] Produce the missed August 2026 issue from July 2026 public-source material.
- [x] Produce the missed September 2026 issue from August 2026 public-source material.
- [x] Run source-health and report-quality checks for each recovered issue.
- [x] Present drafts and rendered PDFs for Jeff's review before external delivery.
- [x] Replace the retired Claude scheduled task with a working Codex-native monthly automation that runs on the first day of each month.
- [x] Preserve the public/unclassified source boundary and the human review gate.
- [x] Correct stale registry and system documentation so the stated runtime matches the deployed runtime.
- [x] Verify the next scheduled time and retain enough evidence to distinguish a missed invocation from a failed run.

## Recovery evidence (2026-09-06)

- August issue: 43 items across six sections; eight-page PDF with 48 links and no empty pages.
- September issue: 47 items across six sections; eight-page PDF with 54 links and no empty pages.
- Automated checks: 69 tests passed; structured-data, duplicate, punctuation, link, PDF-text, and page-render checks completed.
- Scheduler: active Codex automation `spectra-monthly-report`, scheduled for 5:00 AM local time on the first day of each month.
- Delivery: no email or Discord message was sent. Both issues remain behind Jeff's review gate.

## References

- Capability C4 (Integration)
- AI Assistant `docs/runbooks/stream2-briefing-cutover.md`
- SPECTRA `CLAUDE.md`
- AI Assistant project registry (`data/projects.yaml`)

## Resolution

The July migration omitted SPECTRA from the replacement scheduler, so August and September had no invocation or failure receipt. The pipeline now accepts an explicit issue month, constrains source collection to the prior calendar month, uses the repository virtualenv, and renders stable review PDFs. A Codex-native monthly automation (`spectra-monthly-report`) is active for 05:00 local time on the first day of each month. Recovered outputs are `/home/jak3676/src/JAKSecurity/SPECTRA/output/2026-08-SPECTRA.pdf` and `/home/jak3676/src/JAKSecurity/SPECTRA/output/2026-09-SPECTRA.pdf`.

Validation completed on 2026-09-06: 69 SPECTRA tests passed; both recovered issues passed structured-data, duplicate, punctuation, source-health, link, PDF-text, and rendered-page checks. No email or Discord delivery was triggered by the recovery. The remaining open source-quality tickets 003 and 004 are outside this restoration ticket.

Follow-up risk: by December 2026, a scheduler or credential drift could leave the automation configured but unable to produce an artifact. The first-of-month check should confirm the issue-month PDF and health receipt exist before any delivery decision.
