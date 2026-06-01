# Requirements

## Introduction

The `$nightly-ci-safe` skill must preserve the full-CI evidence standard while still preventing uncontrolled repeated full-CI reruns. It must call builder `full-ci` for the one allowed full inventory pass and verify builder's proof gate before declaring success.

## Requirements

### Requirement 1: Full-CI Command Enforcement

**User Story:** As an operator, I want `$nightly-ci-safe` to run the real full-CI path, so a nightly request cannot be satisfied by weaker commands.

#### Acceptance Criteria

1. WHEN `$nightly-ci-safe` starts a full nightly pass THEN it SHALL call builder `full-ci`.
2. WHEN report-only, no-ci, dry-run, sanity, smoke, GitHub-only, or stale reused evidence is available THEN the skill SHALL NOT treat it as a full nightly substitute.
3. WHEN builder `full-ci` is blocked or unavailable THEN the skill SHALL report `full nightly not completed`.

### Requirement 2: Proof Gate Verification

**User Story:** As a reviewer, I want the skill to inspect builder proof metadata, so it cannot summarize invalid evidence as green.

#### Acceptance Criteria

1. WHEN builder finishes THEN the skill SHALL verify builder's full-CI proof gate.
2. WHEN the proof gate fails THEN the skill SHALL report blockers and not claim success.
3. WHEN only candidate-inventory proof exists THEN the skill SHALL label it as non-executed proof, not a passed full nightly.

### Requirement 3: Final Checklist

**User Story:** As a requester, I want a compact final checklist, so I can see exactly what level of validation ran.

#### Acceptance Criteria

1. WHEN the skill finishes THEN it SHALL report command used, run preset, proof status, executed count, not-run count, browser status, builder status, artifact/mirror status when requested, and blockers.
2. WHEN dispatch text asks for nightly-safe/full nightly THEN the skill SHALL preserve the full-CI requirement even under time pressure.

### Requirement 4: Static Regression Coverage

**User Story:** As an agent maintainer, I want tests or validation for the skill text, so future edits do not remove the full-CI guard.

#### Acceptance Criteria

1. WHEN agent tests or static checks run THEN they SHALL verify the skill references builder `full-ci`.
2. WHEN agent tests or static checks run THEN they SHALL verify the forbidden substitution list remains present.
3. WHEN agent tests or static checks run THEN they SHALL verify proof-gate verification is required before success.
