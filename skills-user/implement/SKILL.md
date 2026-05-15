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

