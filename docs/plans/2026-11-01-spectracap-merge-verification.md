# Capture merge verification — 2026-11-01

| ID | Severity | File:line | Finding | Suggested fix |
|---|---|---|---|---|
| V1 | Medium; documentation prerequisite before installation | `README.md:51`, `README.md:124`, `deploy/systemd/spectra-capture.service:8` | The install procedure is not complete for a new operator. The general setup clones into the caller's current directory and runs bare `pip install`, but the service requires Jeff's designated native checkout and its `.venv/bin/python`. Copying the units from an arbitrary repository root does not change those fixed paths. A new operator can enable a timer whose service cannot start. The intended native interpreter does exist and is executable on this machine; this is a reproducibility/documentation defect, not evidence that Jeff's environment is broken. | Before the copy/enable commands, identify the designated native checkout, require checking both service paths, and document `python3 -m venv .venv` plus `.venv/bin/python -m pip install -r requirements.txt` for a fresh checkout. Existing environments should be verified rather than recreated. Document that an alternate installation requires adjusting both service paths. |
| V2 | Low; operational clarification | `README.md:135`, `deploy/systemd/spectra-capture.timer:6` | The catch-up description correctly conditions execution on the user manager starting, but never explains that enabling a user timer alone does not ensure that manager runs before login or after logout. `Persistent=true` neither enables lingering nor wakes a powered-off workstation. A novice can mistake boot for guaranteed execution. | State that execution requires an active user manager; without lingering, login may be the catch-up point. Explain lingering as an optional, separately chosen host setting if unattended execution while logged out is wanted. Do not silently enable it. |
| V3 | Low; inherited, nonblocking | `docs/diagrams/architecture.d2:3`, `docs/diagrams/architecture.d2:44` | The diagram still identifies Claude as the scheduled curator and retains the Anthropic icon, while `README.md:144` identifies the Codex monthly automation. This is the previously documented optional Patch B, not a regression in this merge. | Apply the review's optional Patch B and regenerate both diagram artifacts in a separate documentation change. |

## 1. Held branch versus merged second parent

`debb2bc` has first parent `e7001e1` and second parent `a8f7c2b`.
`git diff codex/q-spectracap debb2bc^2` changes exactly three files:

- `docs/plans/2026-10-31-spectracap-branch-review.md`: the 197-line review document.
- `src/collect/history.py`: the three added lines from Patch A.
- `tests/collect/test_capture.py`: the 15 added lines from Patch A.

There are no other differences. `git diff debb2bc^2 debb2bc` is empty,
so the merge result is also identical to the reviewed second-parent tree.
The merge against its first parent changes 16 implementation/documentation
paths, with no tracked `data/` or `output/` changes.

## 2. Patch A and its regression test

Patch A is present exactly as specified, including its explanatory comment,
canonical capture-filename guard at `src/collect/history.py:28`, and
`test_monthly_without_captures_ignores_unrelated_broken_snapshot` at
`tests/collect/test_capture.py:233`. Both added-text blocks were extracted
from the review and matched against the merged files.

The exact test was executed with only that guard removed from the function
in memory. It failed at `tests/collect/test_capture.py:242`:
`assert short['status'] == 'ok'` received `error`. This is the intended
failure, caused by decoding the unrelated malformed snapshot. No source or
test file was edited. The normal merged test is included in the full-suite
validation below.

The guard deliberately uses the automatic capture naming convention; it
does not promise health aggregation after manually renaming every capture.
Malformed retained files still fail preparation, as they did before the
merge. Patch A preserves collection's no-capture health behavior rather
than claiming to repair malformed input.

## 3. Units and operator installation instructions

The units implement the shared twice-weekly capture decision in
Architecture Decision Record (ADR) 0002 (frequent capture),
`docs/adr/0002-frequent-capture-for-short-feeds.md`. That decision specifies
twice weekly, but does not itself specify weekdays or the hour; Tuesday and
Friday at 06:00 local are specified by the packet, README, and timer.

- `deploy/systemd/spectra-capture.timer:5` contains
  `OnCalendar=Tue,Fri *-*-* 06:00:00`. There is no timezone override, so the
  host's local timezone applies. Offline `systemd-analyze calendar` parsing
  from November 1 produced November 3, 6, 10, and 13 at 06:00 Eastern
  Standard Time (EST), or 11:00 Coordinated Universal Time (UTC). The usual
  systemd timer accuracy tolerance applies; this is not a second-exact
  execution guarantee.
- The README copies both files into the user's unit directory and uses
  `systemctl --user`; `WantedBy=timers.target` enables the timer there.
  The matching basename implicitly selects `spectra-capture.service`.
- `deploy/systemd/spectra-capture.service:7` uses `Type=oneshot`. Lines 8–9
  point to the designated native SPECTRA repository and its
  `.venv/bin/python -m src.collect.capture`, with the repository as working
  directory. These match the packet's native repository. The relative
  default configuration and output paths therefore resolve correctly.
- Neither unit contains credentials, secret environment assignments, or
  delivery commands. The capture source selection is the three intended
  public feeds; the configuration regression test checks that exact set.
- `Persistent=true` records timer activation history and triggers one
  catch-up invocation when an inactive timer is activated after a missed
  calendar event. It does not replay every missed slot or recover rolled-off
  articles. Catch-up runs with the current local date, so it routes to the
  next issue at execution time, not to a historical missed event's issue.
  This interpretation was checked against the installed `systemd.timer(5)`
  documentation. The installed `loginctl(1)` documentation confirms that
  lingering controls user-manager availability at boot and after logout.

The copy, reload, enable, list-timers, and journal commands are appropriate
for an already prepared native checkout. The section is **not complete for
a new operator** because of V1 (setup prerequisite); V2 (manager lifecycle)
should be clarified alongside it. No units were installed, started, or
queried through a live service manager. This review does not establish the
earlier November report's pre-merge existence or authorize installation.

## 4. Monthly behavior without captures

Yes, for the unchanged pipeline behavior with identical source
configuration. The intended source-list changes naturally change which
publishers a monthly run fetches.

`test_monthly_without_captures_preserves_health_and_files` at
`tests/collect/test_capture.py:128` covers empty, partial, and
boundary-reaching responses. It compares capture-enabled and unmarked
configurations of the **new** runner, including result metadata, daily
filenames, health, and absence of a capture ledger. It does not execute the
pre-merge implementation or compare preparation results. The Patch A test
adds the malformed-unrelated-file case. No committed test directly compares
the old and new implementations end to end.

To close that evidence gap for this review, three offline probes loaded the
first parent's runner, save implementation, and preparation code in memory
and compared them with the merge. With a frozen clock and identical mocked
feeds, all three cases passed: empty/unknown coverage, November 3 only
(partial), and October 31 plus November 3 (boundary reached). Results,
filenames, raw snapshot contents, health contents including timestamps,
and prepared items matched exactly after normalizing only temporary output
roots. These are review probes, not newly committed regression tests.

## 5. Diagram size and icons

No node icons were dropped. Comparing the first parent's and merged
Scalable Vector Graphics (SVG) text proves byte equality after exactly
four label substitutions: `17 Sources` to `16 Sources`, `The Record` to
`Krebs`, `AI Research (5)` to `AI Research (4)`, and removal of `The Verge`
from the final source label. Both files have 12 image elements, and all
12 elements are identical, including their image content. The view box is
unchanged at `0 0 3351 1178`; geometry and edges are also unchanged by the
normalized byte comparison.

The Portable Network Graphics (PNG) headers show 647,982 bytes at
6702 × 2356 before the merge and 168,184 bytes at 3351 × 1178 afterward.
The new raster has half the dimensions on each axis and one quarter the
pixel count. This explains the large size reduction without evidence of
lost nodes or icons. The stale curator icon is V3 (diagram labeling), not a
removed icon. This check compared vector content and raster headers; it
does not claim a new visual inspection of the raster.

## 6. Other findings, validation, and disposition

The findings table is ranked by severity. V1 (setup prerequisite) is the
pre-install documentation fix; V2 (manager lifecycle) belongs in the same
operator clarification. V3 (diagram labeling) remains optional and
nonblocking. No additional blocking code defect was found in the merged
diff. The capture retention, aggregate health, deduplication, source
selection, checker, and existing monthly behavior were reviewed against
the requested files and the full earlier review.

Judgment calls: treat the new-operator setup gap as a documentation blocker,
not a reason to redesign capture; retain the accepted observed-gap coverage
model rather than demanding proof of every published article; treat the
lower-resolution raster and inherited curator label as nonblocking; leave
lingering and all live installation decisions to the interactive session.

Validation: the packet's nonempty-report, full-suite, and `git diff --check`
command chain passed with the designated native virtual-environment
interpreter: **229 passed in 0.42 seconds**, including the normal Patch A
regression. Its in-memory mutation separately produced the expected one
failure. All three direct pre-merge compatibility probes passed. There was
no ambient temporary-directory Git failure. An additional whitespace check
against `/dev/null` covered this new, untracked report itself and reported
no whitespace errors.
All probes used mocked inputs and temporary test folders. Bytecode and
pytest cache writes were disabled. No network requests, live service
changes, Git mutations, tracker edits, or repository data/output writes
were performed. The only deliverable is this report, left uncommitted.

Verdict: fix first.
