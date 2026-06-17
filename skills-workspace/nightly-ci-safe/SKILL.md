---
name: nightly-ci-safe
description: Run a safe post-queue nightly CI validation pass without falling into repeated full-CI reruns. Use when the user wants one end-of-night CI run after a queue or implementation batch, wants strict limits on reruns, or explicitly wants to avoid repeating the prior 21-hour CI anti-pattern.
---

# Nightly CI Safe

## Overview

Use this skill for the final nightly CI pass after the current queue or implementation batch is finished.

The goal is to get one truthful failure inventory from full CI, fix failures in batches, rerun only narrowly allowed individual tests, and stop before the session turns into another long uncontrolled verification loop.

## Core Rules

1. Run full CI exactly once after the current undone queue is complete.
2. Never run full CI again in the same nightly run.
3. Fix the whole currently known batch of fixable failures before rerunning anything.
4. Only rerun specifically failed tests whose last known duration is less than 5 minutes each.
5. The rerun batch must include only those previously failing tests that were just fixed.
6. Do not rerun any previously passed test in those targeted rerun batches.
7. Repeat the cycle of `inventory failures -> fix all fixable -> rerun only allowed fixed failures` at most 5 times.
8. If the failed-test inventory reaches zero, treat that as all green for the night; do not spend another full CI run trying to reconfirm it.
9. Prioritize tests added in the scope of the current seed/work and tests most relevant to the artifacts that will ship tonight.
10. For Axolync builder-backed runs, full CI means the builder-owned `full-ci` command/profile. Do not substitute report-only, no-ci, dry-run, sanity, GitHub metadata, or inventory-only evidence when the user asked for full CI.
11. If the user explicitly asks for split GitHub/local proof, use Builder's explicit split flag (`npm run full-ci -- --github-safe-cloud`) rather than running GitHub proof and local proof as detached evidence.
12. A split proof run that falls back from GitHub-safe cloud to local execution is not clean cloud success. Report it as fallback evidence and preserve the Builder report warning.
13. When a post-fix continuation inventory is needed, use the Builder candidate skip-list planner instead of starting another broad full-CI run.

## Workflow

### 1. Finish The Queue First

Do not start this workflow while queue tasks are still incomplete.

### 2. Run Full CI Once

Use the single full-CI pass only to collect the truthful failure inventory.

Do not treat it as the main validation loop.

For Axolync workspaces, the governing command is:

```powershell
npm run full-ci
```

The Builder default full-CI preset is non-fail-fast. Do not add `--fail-fast` unless the user explicitly asks for early termination.

When the requester explicitly wants GitHub-safe tests offloaded to GitHub Actions and GitHub-skipped-local tests run locally, use:

```powershell
npm run full-ci -- --github-safe-cloud
```

Do not use this flag silently. The split mode is an explicit proof mode because it changes where part of the proof is executed.

Before running the expensive pass, verify the same checkout can pass the non-executing proof gate:

```powershell
npm run full-ci -- --dry-run
```

The proof gate is only a candidate inventory check. It is not the full-CI run. It is valid only if it reports `profile=full-ci`, `workflow=local-full`, `source=local-authoritative`, and candidate counts at the configured full-CI scale, including an `axolync-browser` candidate count near the historical local-full baseline rather than the reduced sanity/report scale.

If `npm run full-ci -- --dry-run` fails, stop and report that full-CI proof is blocked. Do not replace it with `report:generate`, `report:noci`, `report:generate:dry`, `sanity`, GitHub run metadata, or a report that is mostly `not_run`.

Capture at least:

- failing tests
- failing suites
- last known durations
- which failures are relevant to the work changed tonight
- `output/latest/reports/full-ci-test-ledger-latest.json`
- `output/latest/reports/full-ci-passed-skip-list-latest.txt`

If you need to materialize the passed-test skip-list from an already completed full-CI report without rerunning full CI, use:

```powershell
npm run full-ci:remaining
```

If the source full-CI report is not `output/latest/reports/ci-latest.json`, pass it explicitly:

```powershell
npm run full-ci:remaining -- --ci-report <path-to-ci-latest.json>
```

The resulting `full-ci-passed-skip-list-latest.txt` is dry-run continuation input, not a claim that another full-CI execution has occurred.

### 3. Partition The Failures

After the full-CI inventory, classify failures into:

- `rerunnable now`
  - individual failing tests
  - each under 5 minutes based on the best known duration data
- `not rerunnable under this skill`
  - tests above 5 minutes
  - failures that cannot be isolated without rerunning previously passed tests
  - failures whose framework only exposes them through broad suite reruns that would violate the rules

If duration data is missing or ambiguous, be conservative and treat the test as not rerunnable under this skill.

### 4. Fix The Whole Current Batch First

Do not rerun tests one by one as each fix lands.

Instead:

1. inspect the whole currently known failure batch
2. fix every failure in that batch that is realistically fixable in the current pass
3. only then prepare the rerun batch

Before any broad continuation after fixes, ask Builder for the dry-run remaining-candidate view instead:

```powershell
npm run full-ci -- --dry-run --skip-list output/latest/reports/full-ci-passed-skip-list-latest.txt
```

If the plan reports zero remaining candidates, do not run another full CI. If it reports remaining candidates, use that output to choose narrow reruns only.

### 5. Rerun Only The Allowed Fixed Failures

The rerun batch must contain only:

- tests that failed in the last inventory
- tests you just fixed
- tests under 5 minutes each

Do not include:

- previously passed tests
- neighboring tests in the same suite just because they are convenient
- a whole CI pass
- a whole suite unless that suite contains only the failing test(s) and still obeys the duration rule

### 6. Repeat At Most 5 Iterations

An iteration means:

1. use the current failure inventory
2. fix the whole current batch
3. rerun only the allowed fixed failures
4. collect the next remaining-failure inventory

Use `npm run full-ci -- --dry-run --skip-list <skip-list>` as the remaining-candidate view. Do not emulate progress by repeatedly rerunning full CI.

Stop after 5 iterations even if failures remain.

### 7. Treat Zero Remaining Failures As Nightly Success

If the current failure inventory reaches zero, stop.

Do not run another full CI to reconfirm it.

The nightly success bar under this skill is:

- there are no currently known failing tests left in the allowed tracked inventory

### 8. Keep Focus On Tonight's Critical Tests

Prioritize:

- tests added in the scope of the current queue or seed work
- tests covering artifacts that will be generated/shipped tonight
- tests directly exercising the changed runtime/build paths

Do not burn the nightly budget chasing broad unrelated failures unless they block the current work from being called green.

## Guardrails

- Do not promote convenience over rule integrity.
- Do not justify a broad rerun with “better safe than sorry.”
- Do not silently exceed the 5-iteration cap.
- Do not drift into a second full-CI run for the same nightly session.
- If a fix might have created some new unrelated regression outside the allowed rerun scope, accept that risk for the night and report it plainly instead of exploding runtime again.
- Do not call a run full-CI proof if builder/browser rows are mostly `not_run`.
- Do not call a report-only/no-ci/sanity run a nightly-safe full run.

## Final Handoff Checklist

When reporting completion, include:

- exact full-CI command used
- whether `npm run full-ci -- --dry-run` passed before the run
- final mirror/report path if mirroring was requested
- per-repo workflow, source, testSource, total, passed, failed, skipped, and not_run counts
- explicit browser local-full or approved-equivalent executed count
- every pushed fix commit, or `none`
- `FULL CI PROOF NOT VALID` if the run used any substituted mode, the proof gate did not pass, candidate/executed counts cannot be reconciled, Browser rows are collapsed instead of individual assertions, or the report is mostly `not_run`

## Dispatch-Specific Guard

If an incoming dispatch explicitly says `$nightly-ci-safe`, `nightly ci safe`, or "full CI", treat the Axolync builder `full-ci` command/profile as mandatory unless the dispatch itself explicitly narrows the scope away from full CI. If the requested checkout cannot run `full-ci`, return a blocker instead of quietly downgrading to report-only, no-ci, dry-run, smoke, sanity, or inventory-only validation.
