# 202: Close out frequent capture for short feeds (ADR 0002)

**Status**: Delivered  **Priority**: P2  **Type**: Chore
**Created**: 2026-11-18
**Capability**: C3

## Summary

ADR 0002 (twice-weekly capture of `cisa_alerts`, `nextgov` and
`dark_reading`) shipped without a backlog row. This ticket owns it and
closes the leftovers. Handed over by AI Assistant AIA-291 (Codex queue
leftovers) and the 2026-11 to-do item V.

The to-do asked to merge the held Codex branch `codex/q-spectracap`
(`c33aacd`) and then install its timer. Neither step was needed:

- The same work was relanded as `spectracap2` (`a8f7c2b`) and merged to
  `main` in `debb2bc` on 2026-11-01. `git diff c33aacd a8f7c2b` adds only
  the branch review, a three-line guard in `src/collect/history.py` and its
  regression test (see `docs/plans/2026-11-01-spectracap-merge-verification.md`).
  Everything else `c33aacd` differs from `main` by is later work on `main`
  (install docs, the diagram relabel, the sandbox network notes in
  `AGENTS.md`). Merging it would have changed no file, so it was not merged;
  the branch and its queue worktree were deleted instead.
- The user timer has been installed since 2026-11-09. The files in
  `~/.config/systemd/user/` are identical to `deploy/systemd/`.

## Network fit

The capture unit runs as a plain user service with the host's normal
network. The `.codex/config.toml` network setting only applies inside the
Codex sandbox that runs the monthly automation, so the capture unit needs
no sandbox setup and the monthly run is unchanged.

## Acceptance

- [x] Capture code, units and docs on `origin/main` (`debb2bc`, 2026-11-01).
- [x] Timer enabled and active; next run Fri 2026-11-20 06:00.
- [x] Captures succeed: journal shows `cisa_alerts`, `nextgov` and
      `dark_reading` all `ok` on 2026-11-10, 11-13, 11-17 and a manual run
      at 2026-11-18 22:32.
- [x] Full test suite passes on `main` (231 passed, 2026-11-18).
- [x] `codex/q-spectracap` branch and queue worktree removed.
- [x] `docs/diagrams/architecture.svg` regenerated from `architecture.d2`
      (2026-11-19). Commit `43a14b9` had relabeled the curator from Claude to
      Codex and marked delivery "after approval" in the source only. Jeff
      approved installing d2 (v0.9.0, checksum verified, `~/.local/bin/d2`).
      The house theme the source imported from the retired
      `~/.claude/skills/d2-diagram/` path now lives beside it as
      `docs/diagrams/jak-dark.d2`. The stale `architecture.png` was removed
      rather than regenerated: nothing references it, the house standard ships
      only `.d2` and `.svg`, and d2's PNG export would download a Chromium build.
