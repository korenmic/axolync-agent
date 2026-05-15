# Requirements

## Introduction

The implement user skill provides a short command for running all intended undone enqueued tasks through `$tactic`, using `$notify` for progress visibility, and pushing the resulting committed work to the agreed branch.

The source seed is `project-seeds/04-implement-user-skill.md`.

## Requirements

### Requirement 1: User Skill Placement And Role

**User Story:** As an agent maintainer, I want `$implement` to live in the agents repo user-skill source area, so it can be installed consistently and used as the standard implementation shortcut.

#### Acceptance Criteria

1. WHEN the skill is created THEN the skill source SHALL live under `axolync-agent/skills-user/implement`.
2. WHEN the skill is created THEN it SHALL NOT live under `skills-workspace`.
3. WHEN the skill is invoked THEN `$implement` SHALL be the canonical invocation.
4. WHEN the skill runs THEN it SHALL act as a workflow wrapper over `$tactic` and `$notify`.
5. WHEN the skill runs THEN it SHALL NOT replace, redefine, or bypass TACTIC's implementation discipline.
6. WHEN the user asks only to enqueue, review, inspect status, or plan THEN `$implement` SHALL NOT run.

### Requirement 2: Task Source Resolution

**User Story:** As a user with a prepared queue, I want `$implement` to run the currently undone enqueued tasks, so I do not need to restate the task list.

#### Acceptance Criteria

1. WHEN `$implement` runs without a more specific task target THEN it SHALL use the current workspace queue as the task source.
2. WHEN the user supplies a specific implementation target THEN `$implement` SHALL pass that target to `$tactic`.
3. WHEN the queue is the task source THEN only undone enqueued tasks SHALL be selected.
4. WHEN no undone enqueued tasks exist THEN `$implement` SHALL report that there is nothing to implement and SHALL NOT push.
5. WHEN `$implement` resolves its task source THEN it SHALL NOT scan unrelated specs or backlogs for extra work.

### Requirement 3: TACTIC Delegation

**User Story:** As a maintainer, I want `$implement` to preserve TACTIC behavior exactly, so the shortcut does not become a second implementation engine.

#### Acceptance Criteria

1. WHEN `$implement` invokes `$tactic` THEN it SHALL forward additional user arguments to `$tactic`.
2. WHEN no tactic mode is specified THEN `$implement` SHALL let `$tactic` use its normal mode inference.
3. WHEN `$tactic` executes tasks THEN `$implement` SHALL preserve TACTIC's one-task-one-commit rule.
4. WHEN `$tactic` encounters blockers THEN `$implement` SHALL preserve TACTIC's original blocker handling.
5. WHEN `$tactic` performs integrity recovery THEN `$implement` SHALL not override or weaken that recovery logic.

### Requirement 4: Worktree State Handling

**User Story:** As a user running implementation work, I want `$implement` to surface dirty worktree risk without changing TACTIC semantics, so I know the state but TACTIC remains the authority.

#### Acceptance Criteria

1. WHEN `$implement` starts and one or more relevant worktrees are dirty THEN it SHALL warn that the worktree is not clean.
2. WHEN a dirty worktree is detected THEN `$implement` SHALL still allow `$tactic` to proceed unless `$tactic` itself stops.
3. WHEN `$tactic` handles dirty or related state THEN `$implement` SHALL not reinterpret or refactor TACTIC behavior.
4. WHEN the dirty state is catastrophic or contradictory THEN the run SHALL stop according to TACTIC's stop conditions.

### Requirement 5: Notifications

**User Story:** As a user waiting on a queued implementation run, I want consistent notifications for start, progress, completion, blockers, and push, so I can monitor the run without watching the terminal.

#### Acceptance Criteria

1. WHEN `$implement` starts THEN it SHALL use `$notify` to send a start notification.
2. WHEN each task starts, progresses, and completes THEN notifications SHALL be sent as supported by `$tactic` and `$notify`.
3. WHEN blockers stop the runnable queue THEN `$implement` SHALL notify with a concise blocker summary.
4. WHEN all tasks finish THEN `$implement` SHALL notify completion before attempting push.
5. WHEN the final push completes THEN `$implement` SHALL send a separate push-complete notification.

### Requirement 6: Push Behavior

**User Story:** As a user, I want `$implement` to push only completed committed work to the intended branch, so implementation runs end in a shareable branch state.

#### Acceptance Criteria

1. WHEN all runnable undone tasks complete and are committed THEN `$implement` SHALL push the resulting work.
2. WHEN a target branch was explicitly agreed in the conversation or dispatch context THEN `$implement` SHALL push to that branch.
3. WHEN no target branch was explicitly agreed THEN `$implement` SHALL infer `master` or the current branch from context.
4. WHEN branch inference is unsafe or ambiguous THEN `$implement` SHALL ask for clarification before pushing.
5. WHEN pushing THEN `$implement` SHALL not silently create a new branch unless the user or context explicitly chose that branch.
6. WHEN push fails THEN `$implement` SHALL report the exact blocker and SHALL NOT claim completion.

### Requirement 7: Documentation And Tests

**User Story:** As a maintainer, I want the skill documented and regression-tested enough to keep it a thin wrapper, so future changes do not drift into a second task runner.

#### Acceptance Criteria

1. WHEN the skill is implemented THEN its docs SHALL state that it delegates implementation to `$tactic`.
2. WHEN the skill is implemented THEN its docs SHALL state that extra arguments are forwarded to `$tactic`.
3. WHEN the skill is implemented THEN its docs SHALL state that dirty worktrees produce warnings but TACTIC remains the handler.
4. WHEN tests are added THEN they SHALL cover argument forwarding.
5. WHEN tests are added THEN they SHALL cover no-undone-task no-op behavior.
6. WHEN tests are added THEN they SHALL cover branch selection and push-blocker reporting.
