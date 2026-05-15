# Design

## Overview

`$implement` is a thin user-skill wrapper for the standard implementation handoff:

1. resolve the current implementation target, normally undone queued tasks
2. invoke `$tactic` with any extra arguments forwarded
3. use `$notify` for start/progress/done/push visibility
4. push committed work to the intended branch after successful completion

It must not become a parallel implementation engine. TACTIC remains responsible for task ordering, one-task-one-commit discipline, blocker handling, verification, markdown task ticking, and integrity recovery.

## Skill Location

The skill source lives at:

`axolync-agent/skills-user/implement`

The canonical invocation is `$implement`. This is a user skill, not a workspace skill, because it is meant to be installed and reused across agents.

## Invocation Model

The skill accepts:

- no explicit target: use the current workspace queue's undone enqueued tasks
- explicit target: pass the target to `$tactic`
- extra arguments: forward them to `$tactic` unchanged

Examples:

```text
$implement
$implement autonomous
$implement tasks 3-5 regular
```

`$implement` does not reinterpret TACTIC modes. If no mode is supplied, TACTIC's own inference applies.

## Queue Scope

When using the queue, the source is the current workspace queue. The skill selects undone enqueued tasks only. It does not scan unrelated specs, backlogs, or repos for extra work.

If there are no undone enqueued tasks, the skill reports a no-op and does not push.

## Worktree Warning

Before invoking TACTIC, the skill may inspect relevant worktree status. If dirty state is detected, it warns the user/terminal/session note.

The warning is informational. `$implement` does not block or recover dirty state itself. TACTIC remains the authority for whether dirty-but-related state can proceed, whether integrity recovery is needed, or whether catastrophic state requires stopping.

## Notification Flow

Use `$notify` for:

- implementation start
- task start/progress/done events as supported through TACTIC/notify
- blockers
- all-tasks-finished
- push-complete

The final push notification is separate from the TACTIC finish notification because it proves the branch handoff is complete.

## Push Flow

Push only after all runnable undone tasks are complete and committed.

Branch selection priority:

1. explicitly agreed branch from prompt/conversation/dispatch context
2. current context branch when already established as the implementation target
3. `master` when context indicates normal master work

If branch inference is unsafe, ask before pushing. Do not silently create a new branch.

If push fails, report the exact command-level or git-level blocker and do not claim completion.

## Safety Boundaries

`$implement` should not run for:

- queue status inspection
- enqueue-only requests
- CRPR review requests
- build/report/mirror requests
- planning-only requests

It is high-impact because it can modify code, commit, and push.

## Testing

Tests can focus on the wrapper contract rather than re-testing TACTIC internals:

- argument forwarding to TACTIC
- no-undone-task no-op
- dirty worktree warning does not block
- branch selection priority
- push blocker reporting
- notify event sequence at wrapper boundaries

## Self-Review Notes

- The design forwards extra arguments instead of inventing a new mode parser.
- The design warns on dirty worktrees but leaves handling to TACTIC.
- The design keeps push after completion and committed proof only.
- The design blocks branch creation unless explicit context authorizes it.
