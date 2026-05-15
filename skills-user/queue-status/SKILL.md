---
name: queue-status
description: Report the status of the current workspace task queue without executing or mutating tasks. Use when invoked as $queue-status, queue-status, or when the user asks how many queue tasks are done, undone, by-reference, by-value, blocked, skipped, or unrecognized.
---

# Queue Status

Use this skill to inspect a workspace task queue and report its current health.

This skill is read-only. It must not:

- start queued work
- run TACTIC
- reorder queue items
- mark queue items done
- rewrite queue records

## Default Queue Discovery

Prefer the current workspace root as the base path.

The parser checks these paths in order:

1. `<workspace-root>/.codex/local-task-queue.md`
2. `<workspace-root>/.codex/tmp/execution-queue.json`

If both exist, the Markdown queue is treated as the active queue and the JSON queue is reported as an additional discovered artifact.

If no queue is found by script discovery, use explicit user/context fallback only when the current conversation or workspace notes name a queue path. Validate that path exists before parsing it.

## Run The Parser

Use the script relative to this skill:

```powershell
python scripts/queue_status.py --workspace-root <workspace-root>
python scripts/queue_status.py --queue-path <path-to-queue>
```

The parser prints a concise human-readable report. It does not persist a second machine-readable status artifact by default because the queue file is already the source data.

## Queue Authority

Queue-local state is authoritative for queue-status counts.

For by-reference records, referenced `tasks.md` files are optional drift evidence only:

- un-enqueued source tasks must not affect queue-status counts
- missing references should be reported, not treated as fatal
- source/queue completion mismatch should be reported as drift without changing counts

## Report Expectations

The report should include:

- queue path and discovery method
- total queued records
- done and undone counts
- ready, active, blocked, skipped, and unknown status counts
- by-reference, by-value, and unrecognized classification counts
- missing reference count
- duplicate/history warnings
- parser gaps that need AI classification
