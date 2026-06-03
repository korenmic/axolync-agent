# Requirements

## Introduction

The agent-owned `$nightly-ci-safe` skill must align with Builder's corrected full-CI command model. It must use candidate dry-runs only as preflight/listing evidence, never as executed proof.

## Requirements

### Requirement 1: Correct Builder Vocabulary

**User Story:** As an operator, I want `$nightly-ci-safe` to call the correct Builder commands, so it cannot use stale inventory-only terminology.

#### Acceptance Criteria

1. WHEN the skill describes preflight candidate listing THEN it SHALL use `npm run full-ci -- --dry-run`.
2. WHEN the skill describes the full validation pass THEN it SHALL use `npm run full-ci`.
3. WHEN the skill describes continuation after fixes THEN it SHALL use `npm run full-ci:remaining`.
4. WHEN the skill text is searched THEN it SHALL NOT reference `full-ci:inventory`.

### Requirement 2: Preserve One-Full-Run Safety

**User Story:** As a maintainer, I want nightly-safe to stay bounded, so it does not repeat the prior long full-CI loop.

#### Acceptance Criteria

1. WHEN nightly-safe runs THEN it SHALL allow at most one broad `npm run full-ci` pass.
2. WHEN failures are fixed afterward THEN it SHALL use strict remaining-test evidence and focused reruns only.
3. WHEN no focused rerun is possible THEN it SHALL report blockers instead of starting another broad full-CI run.

### Requirement 3: Reject Invalid Proof

**User Story:** As a reviewer, I want the agent to report invalid full-CI proof plainly, so reduced or unreconciled evidence is not summarized as green.

#### Acceptance Criteria

1. WHEN Builder reports unreconciled candidate/executed counts THEN nightly-safe SHALL report `FULL CI PROOF NOT VALID`.
2. WHEN evidence is report-only, no-ci, sanity, dry-run, GitHub-only, or mostly `not_run` THEN nightly-safe SHALL NOT call it full-CI success.
3. WHEN Browser rows are collapsed or undercounted relative to candidates THEN nightly-safe SHALL report invalid proof.

## Open Questions

None.

