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

## Workflow

### 1. Finish The Queue First

Do not start this workflow while queue tasks are still incomplete.

### 2. Run Full CI Once

Use the single full-CI pass only to collect the truthful failure inventory.

Do not treat it as the main validation loop.

Capture at least:

- failing tests
- failing suites
- last known durations
- which failures are relevant to the work changed tonight

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
