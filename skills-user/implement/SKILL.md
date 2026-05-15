---
name: implement
description: Run the current workspace's undone enqueued implementation tasks through $tactic with $notify progress, then push committed work to the agreed or context branch. Use when invoked as $implement or when the user asks to implement all queued/undone tasks and push.
---

# Implement

Use this skill as a thin wrapper around `$tactic` and `$notify`.

`$implement` means:

```text
Implement all undone enqueued tasks using $tactic, $notify on each task's start, progress, and done; when all tasks finish, push the work to the agreed-upon branch. If no branch was agreed, push to master or the current branch according to context. Notify again when the push completes.
```

This skill must not replace or reinterpret TACTIC. TACTIC remains responsible for task execution, verification, one-task-one-commit boundaries, blocker handling, and integrity recovery.

## Do Not Use For

- CRPR review
- queue status inspection
- enqueue-only requests
- build/report/mirror requests
- planning-only requests

## High-Level Flow

1. Resolve the current workspace and active queue.
2. Warn if relevant worktrees are dirty.
3. Invoke `$tactic` for the intended undone enqueued tasks.
4. Preserve all TACTIC rules, including per-task commits.
5. Push committed work to the agreed/current/master branch as context dictates.
6. Notify when the push completes.

## Task Source And TACTIC Arguments

When no extra target or mode is supplied, treat the task source as the current workspace's undone enqueued tasks.

When the user supplies additional arguments after `$implement`, forward them to `$tactic` unchanged. Do not parse new implementation modes in this skill; `$tactic` owns mode inference and task-source semantics.

Examples:

```text
$implement
$implement autonomous
$implement autonomous --only Q-100
```

## Dirty Worktree Warning

Before invoking `$tactic`, inspect relevant worktrees when practical. If a worktree is dirty, warn clearly:

```text
Warning: worktree is not clean: <repo>. Proceeding leaves dirty-state handling to $tactic.
```

Do not block solely because of dirty state. `$tactic` owns dirty-state handling, integrity recovery, and catastrophic stop decisions.

## Notify Integration

Use `$notify` for wrapper-level events and preserve TACTIC's own per-task notifications.

Required events:

- implementation start
- TACTIC task start
- TACTIC task progress
- TACTIC task done
- blocker stop
- all tasks finished
- push complete

The push-complete notification is separate from the TACTIC finish notification because it confirms the branch handoff completed.

## Push Behavior

Push only after all runnable undone tasks are complete and committed.

Branch priority:

1. explicitly agreed branch from the current prompt, conversation, or dispatch context
2. current context branch when already established as the implementation target
3. `master` when context indicates normal master work

If branch inference is unsafe, ask before pushing. Do not silently create a new branch. If push fails, report the exact blocker and do not send a push-complete notification.

## Verification

When changing this skill, run:

```powershell
python -m unittest tests.test_implement -v
```

For a broader queue-workflow check, run:

```powershell
python -m unittest tests.test_queue_status tests.test_enqueue tests.test_implement -v
```

## Authority Boundaries

- `$tactic` owns task execution and commit discipline.
- `$notify` owns notification transport and formatting defaults.
- `$enqueue` owns adding new queue records.
- `$queue-status` owns read-only queue health reporting.
- `$implement` owns only the wrapper handoff, final push decision, and push-complete notification.
