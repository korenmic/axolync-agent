# Requirements

## Introduction

This spec implements seed `188-p1-temp-headless-smoke-skill.md`: a workspace skill that authorizes safe, temporary, untracked headless-browser smoke tests on a non-default local server, with mandatory cleanup and test reporting.

## Requirements

### Requirement 1: Workspace Skill Placement

**User Story:** As an Axolync maintainer, I want `$temp-headless-smoke` to be a workspace skill, so agents can use it for Axolync workspace runtime checks without installing anything into the user Codex homedir.

#### Acceptance Criteria

1. WHEN the skill is implemented THEN it SHALL live under `skills-workspace/temp-headless-smoke`.
2. WHEN the skill is implemented THEN it SHALL NOT create or modify `~/.codex/skills`.
3. WHEN the skill is listed by `$lssa` THEN `temp-headless-smoke` SHALL appear under `skills-workspace`.
4. The skill frontmatter SHALL use name `temp-headless-smoke`.

### Requirement 2: Runner-Owned Temporary Test Design

**User Story:** As a user, I want the agent to design relevant temporary smoke tests from the current feature context, so I do not need to provide scripts or exact click paths.

#### Acceptance Criteria

1. WHEN `$temp-headless-smoke` is invoked THEN the agent SHALL infer relevant headless smoke tests from the current task, latest agreed design, and suspected risk areas.
2. WHEN the behavior is not ambiguous THEN the agent SHALL NOT require the user to provide exact test scripts, click paths, or assertions.
3. WHEN behavior is genuinely ambiguous or risky THEN the agent MAY ask for focused clarification before running tests.
4. The skill SHALL keep temporary tests scoped to the current proof target.

### Requirement 3: Temporary Server Safety

**User Story:** As a user running their own dev server, I want temporary smoke tests to avoid the default port and clean up after themselves.

#### Acceptance Criteria

1. WHEN the skill starts a server THEN it SHALL use a non-default port.
2. WHEN a user provides a specific temporary port THEN the skill MAY use it after checking availability.
3. WHEN no port is provided THEN the skill SHALL choose a high-numbered available local port.
4. WHEN the skill finishes or fails after server start THEN it SHALL attempt to kill the temporary server.
5. WHEN the skill reports results THEN it SHALL state the temporary port used.

### Requirement 4: Temporary Script Hygiene

**User Story:** As a maintainer, I want smoke-test automation to stay temporary unless explicitly promoted.

#### Acceptance Criteria

1. WHEN the skill creates automation scripts THEN they SHALL be untracked temporary files.
2. WHEN the skill finishes THEN it SHALL remove temporary scripts/logs unless the user asks to keep them.
3. WHEN a temporary test proves useful THEN the skill MAY recommend converting it into committed test coverage.
4. The skill SHALL NOT commit temporary scripts unless the user explicitly asks.

### Requirement 5: Bug Fix And Retest Authorization

**User Story:** As a user, I want an agent to fix bugs discovered by temporary smoke tests without waiting for another approval round.

#### Acceptance Criteria

1. WHEN a temporary smoke test proves a bug in the latest agreed design THEN the skill MAY fix that bug immediately.
2. WHEN the skill fixes such a bug THEN it SHALL rerun the relevant temporary test.
3. WHEN the test passes after the fix THEN the skill SHALL report the fix and retest.
4. The skill SHALL NOT expand into unrelated cleanup or behavior changes.

### Requirement 6: Reporting And Merge-Gate Honesty

**User Story:** As a maintainer, I want temporary smoke-test evidence reported clearly without overstating merge readiness.

#### Acceptance Criteria

1. WHEN the skill completes THEN it SHALL list each temporary test performed.
2. WHEN commands or scripts were used THEN it SHALL summarize them.
3. WHEN bugs were found or fixed THEN it SHALL report them.
4. WHEN committed tests, CI, or rebuilds are still required THEN the skill SHALL say so.
5. The skill SHALL NOT claim merge readiness from temporary tests alone when stronger gates are required.

