# Sinq2 Queue Logic Summary

This note summarizes the current queueing logic I use in this workspace family.
It is based on the global `TACTIC` and `notify` skills installed under `~/.codex`.

## Core Idea

Treat multi-task work as a disciplined queue runner, not as an open-ended "keep hacking until done" loop.

The queue runner is optimized for:

- one task at a time
- resumability
- durable handoff to another agent
- clear blocker handling
- per-task proof boundaries
- progress visibility

It is less optimized for:

- fuzzy exploratory work with no stable task boundaries
- giant mixed changesets
- silently improvising across multiple unrelated tasks at once

## Modes

There are two modes.

### 1. Autonomous

- Run the full scoped queue end-to-end.
- Answer non-catastrophic logic questions yourself.
- Stop only for catastrophic environment/workspace failures or truly catastrophic ambiguity.

Use when the user wants a hands-off run.

### 2. Regular

- Ask known blocking questions before starting.
- If a blocker appears mid-run, move that task and its dependents to the end of the queue.
- Continue all other runnable work.
- Only raise the remaining blocking questions after runnable work is exhausted.

Use when the user wants safer human checkpoints.

## Task Source Resolution

Pick the queue from the most explicit source available.

Priority order:

1. Explicit queue or mixed task bundle in the current prompt/context
2. Explicit file list already established in context
3. Current spec `tasks.md` when the session is clearly about that spec

If still ambiguous:

- in regular mode: ask before starting
- in autonomous mode: choose the most explicit plausible source and record that assumption

## Session State

Keep live queue state in:

- `<workspaceRoot>/.codex/tactic/session.json`

Use repo root when in a repo; otherwise use current working directory.

The state is meant to let another agent resume without guessing.

Track at least:

- mode
- task source summary
- total task count
- ordered task list
- current task index
- completed task ids
- blocked task ids
- dependency deferrals
- session start timestamp
- current task start timestamp
- last completed task duration
- total elapsed session duration
- last notification timestamp
- short recent note

Important detail:

- even memory-only tasks should get stable ids and stable text in the session file

## Execution Discipline

The mnemonic is:

- `T` = Task first
- `A` = Apply scoped code and tests
- `C` = Confirm with local verification
- `T` = Tick the completed checkbox if the source is markdown-backed
- `I` = Integrate as one scoped task commit
- `C` = Communicate progress with notifications

Practical loop:

1. Pick the current task from the ordered queue.
2. Work only on that task.
3. Add/update tests for that task.
4. Run verification for that task.
5. If the source is `tasks.md` / backlog markdown, check only the completed task item.
6. Stage code + tests + task-file proof together.
7. Commit exactly once per completed task.

This logic strongly prefers one-task-per-commit.

## Commit Policy

Use the task text itself as the commit-message source.

- If the task came from markdown, use the original task description as directly as practical.
- If the task came from memory/context, first materialize stable task text in `session.json`, then commit from that.

Do not bundle multiple finished tasks into one commit.

## Blocker Policy

### In autonomous mode

- Resolve logic blockers yourself unless they are catastrophic.
- Stop for catastrophic workspace-state anomalies, destructive contradictions, or environment breakage.

### In regular mode

- Ask known blockers before starting.
- Mid-run blockers are deferred, not allowed to stall the whole queue.
- Also defer dependent tasks.
- At end-of-runnable-work, raise one consolidated blocker handoff instead of drip-feeding questions.

## Notification Policy

Use the global `notify` skill / CLI.

Default events:

- `start`
- after every completed task
- `block` when regular mode exhausts runnable work but blockers remain
- `finish`

Default message shape:

```text
<Bot Name>: out of total X tasks - [D done / C current / R remaining]; last task <duration>, session <duration> - <optional short note>
```

Defaults:

- bot name comes from `AXOLYNC_NOTIFY_BOT_NAME`, then `~/bin/notify-config.json`, then `Codex`
- optional note should stay under one short sentence
- `start` may use `n/a` for last-task duration

## Stop Conditions

Hard stop on catastrophic workspace-state failures.

Examples:

- repositories or directories suddenly disappear
- persistent files look corrupted or massively rewritten unexpectedly
- environment/tooling breaks in a way that makes further writes unsafe

Important rule:

- do not self-heal or recreate damaged state during queue execution

## Design Biases

This queue logic is opinionated.

What it optimizes for:

- resume by another agent
- durable progress accounting
- minimal ambiguity about "what was completed"
- minimal ambiguity about "what is blocked"
- clean commit history

What it intentionally avoids:

- multitasking inside a single proof step
- giant unscoped commits
- turning blockers into total session deadlocks
- silently overriding catastrophic anomalies

## Short Merge-Friendly Summary

If another agent needs the shortest possible description:

`Sinq2 queue logic = resolve the most explicit task source, choose autonomous or regular mode, persist queue/session state in .codex/tactic/session.json, execute exactly one task at a time with tests + verification + optional checkbox update + one commit, defer blockers to the queue end in regular mode, self-resolve non-catastrophic logic blockers in autonomous mode, notify on start/task/block/finish, and hard-stop on catastrophic workspace-state anomalies.`

## Known Tradeoffs

- Strong on implementation queues, weaker on fuzzy research queues.
- Strong on resumability, slightly heavier-weight than ad hoc task running.
- Strong on auditability, but assumes task text is stable enough to become commit text.
- Assumes queue order matters and that dependency deferral can be modeled explicitly.
