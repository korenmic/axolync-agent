# Requirements

## Introduction

The implement PR CI regression gate hardens the `$implement` user skill so PR-targeted implementation sessions do not finish while the pushed PR head has newly red GitHub checks caused by the implementation work.

The source seed is `project-seeds/08-p0-implement-pr-ci-regression-gate.md`.

## Requirements

### Requirement 1: PR CI Gate Applicability

**User Story:** As a user receiving a pushed implementation PR, I want `$implement` to check the PR's GitHub CI before reporting completion, so I am not handed a branch with newly introduced red checks.

#### Acceptance Criteria

1. WHEN `$implement` pushes to a PR-targeted branch THEN it SHALL run a PR CI regression gate after the push.
2. WHEN `$implement` runs for local-only, no-push, or non-PR master work THEN the PR CI gate SHALL NOT be mandatory unless the user explicitly requests it.
3. WHEN a PR cannot be identified for the pushed branch THEN `$implement` SHALL report that PR CI verification is unavailable or unknown instead of claiming PR check success.
4. WHEN the PR CI gate applies THEN the push-complete/ready handoff SHALL occur only after the gate result is acceptable.

### Requirement 2: Baseline And Post-Push Check Handling

**User Story:** As an implementer, I want the skill to distinguish newly introduced failures from pre-existing check failures, so the handoff is accurate and actionable.

#### Acceptance Criteria

1. WHEN a PR CI gate starts THEN it SHALL treat baseline check lookup as best-effort.
2. WHEN baseline checks are available THEN the gate SHALL preserve each check's prior conclusion.
3. WHEN post-push checks are available THEN the gate SHALL preserve each current conclusion.
4. WHEN baseline lookup is unavailable THEN the gate SHALL still classify post-push failures instead of ignoring them.
5. WHEN a previously passing check fails after the push THEN the gate SHALL classify it as a PR-caused regression unless explicitly marked unrelated.

### Requirement 3: Failure Ownership And Handoff Semantics

**User Story:** As a user, I want PR-caused CI regressions to remain in the implement session's scope, so delivery responsibility includes fixing tests the PR broke.

#### Acceptance Criteria

1. WHEN the gate classifies a check as a PR-caused regression THEN `$implement` SHALL report the regression as a blocker.
2. WHEN PR-caused regressions remain THEN `$implement` SHALL NOT send a successful push-complete/ready notification.
3. WHEN failures are pre-existing, unrelated, or environmental THEN `$implement` SHALL report that classification and the evidence.
4. WHEN check status is unknown or unavailable THEN `$implement` SHALL report the uncertainty explicitly.
5. WHEN all post-push PR checks pass THEN `$implement` MAY report the pushed PR as CI-clean.

### Requirement 4: Skill Documentation Integration

**User Story:** As a maintainer, I want the `$implement` skill docs to describe the CI gate without turning `$implement` into a second implementation engine, so the existing TACTIC boundaries remain intact.

#### Acceptance Criteria

1. WHEN the skill docs describe high-level flow THEN they SHALL include the PR CI gate after push and before completion handoff.
2. WHEN the docs describe authority boundaries THEN they SHALL keep `$tactic` as task execution owner.
3. WHEN the docs describe authority boundaries THEN they SHALL keep `$notify` as notification transport owner.
4. WHEN the docs describe `$implement` ownership THEN they SHALL include final push and PR CI handoff validation.
5. WHEN the docs describe the gate THEN they SHALL state that unavailable GitHub checks are reported, not silently treated as success.

### Requirement 5: Deterministic Helper Coverage

**User Story:** As a maintainer, I want small deterministic helpers for the gate decision model, so the behavior is unit-tested without calling GitHub.

#### Acceptance Criteria

1. WHEN helper code is added THEN it SHALL model check names, baseline conclusions, and post-push conclusions.
2. WHEN all post-push checks pass THEN tests SHALL verify a passing gate result.
3. WHEN a previously passing check fails after push THEN tests SHALL verify a PR-caused regression result.
4. WHEN a check was already failing before push THEN tests SHALL verify a pre-existing failure result unless the result is explicitly marked PR-caused.
5. WHEN check data is unavailable THEN tests SHALL verify an unknown/unavailable result.
6. WHEN formatting gate output THEN tests SHALL verify blocker details remain visible.
