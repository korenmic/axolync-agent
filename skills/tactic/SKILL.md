---
name: tactic
description: Execute a queue of coding tasks from the most explicit current task source, including mixed task bundles, backlog lists, and spec tasks.md files. Use when the user asks to run multiple tasks, says TACTIC, asks for autonomous tactic, or wants a regular multi-task pass that defers blockers until the end. Do not use when the user explicitly says workspace-tactic; in that case, read and follow the repo-local tactic or workflow docs instead.
---

# TACTIC

## Overview

Use this skill as the default cross-workspace meaning of `TACTIC`.

Treat `TACTIC` as a disciplined queue runner for multi-task implementation work. Pick the right task source, track session state in the active workspace, complete one task at a time, notify on progress, and keep moving unless a catastrophic stop condition is reached.

If the user explicitly says `workspace-tactic`, do not apply this global skill by default. Read the repo-local tactic or workflow docs and follow those instructions instead.

## Choose The Mode

Pick one of two modes before starting:

- `autonomous`: run the scoped queue end-to-end, answer non-catastrophic logic blockers yourself, and stop only for catastrophic environment or workspace-state failures or truly catastrophic ambiguity.
- `regular`: ask known blocking questions before starting. If a blocker appears mid-run, move that task and any dependents to the queue end, continue all non-blocked work, and raise the remaining blocking questions only after runnable work is exhausted.

When the user names the mode, follow it. If the user does not name the mode:

- infer `autonomous` when the user asks for a hands-off end-to-end run
- otherwise infer `regular`

## Resolve The Task Source

Resolve the queue from the most explicit source available:

1. An explicit queue or mixed task bundle stated in the current prompt or already-established context
2. An explicit file list already established in context
3. The current spec `tasks.md` if the session is clearly executing that spec

If the source is ambiguous:

- in `regular` mode, ask before starting
- in `autonomous` mode, choose the most explicit plausible source and record that assumption in the session note

Treat the current context as authoritative. If the user already established the active backlog, spec, or mixed queue earlier in the thread, do not ask the user to restate it.

## Create And Maintain Session State

Store live state at `<workspaceRoot>/.codex/tactic/session.json`.

Use the active workspace root. In a repo, use the repo root. Outside a repo, use the current working directory.

Keep the state file current enough that another agent can resume the run. Track at least:

- `mode`
- `taskSource`
- `totalTasks`
- `tasks`
- `currentTaskIndex`
- `completedTaskIds`
- `blockedTaskIds`
- `dependencyDeferrals`
- `sessionStartedAt`
- `currentTaskStartedAt`
- `lastCompletedTaskDuration`
- `totalElapsedDuration`
- `lastNotificationAt`
- `recentNote`

Represent tasks in a stable order. Give each task a stable id even if the source is a memory-only queue. If the source is memory-only, materialize the exact task text in the session state before using it for commits or notifications.

## Run The Queue

Apply the `TACTIC` mnemonic for implementation tasks:

- `T` = Task first
- `A` = Apply the scoped code and tests
- `C` = Confirm with local verification
- `T` = Tick the completed checkbox in the same proof commit when the source is markdown-backed
- `I` = Integrate it as one scoped task commit
- `C` = Communicate progress with notifications

Run one task at a time:

1. Select the current task from the ordered queue.
2. Implement only that task's scoped code changes.
3. Add or update tests for that task.
4. Run the relevant verification for that task.
5. If the task came from `tasks.md` or backlog markdown, check only the completed task item in the same proof change.
6. Stage code, tests, and the checked task file together.
7. Commit once per completed task.

## Per-Task Commit Gate

A task is not complete until all of the following are true:

1. the relevant verification for that task passed
2. the markdown/task state was updated if needed
3. the proof changes for that task were committed
4. the touched repo worktrees are clean enough to begin the next task

Do not mark a task complete in `session.json` and do not send a task-complete notification before that commit exists.

## Commit Rule

Use the task text itself as the commit message source.

- If the task came from markdown, copy the original task description into the commit subject and body as directly as practical.
- If the task came from memory-only context, first materialize the stable task text in `session.json`, then use that text for the commit.

Do not combine multiple finished tasks into one commit. Keep the proof boundary aligned with the completed task.

If one task legitimately spans multiple repos, it still counts as one task boundary:

- commit the repo changes for that one task before starting the next task
- do not use a later task as justification to keep earlier-task changes uncommitted

## TACTIC Integrity Recovery

If you realize the run has drifted away from strict one-task-one-commit boundaries, do not continue silently and do not stop waiting for the user in `autonomous` mode.

Instead:

1. pause advancement to the next queued task
2. inspect the current dirty state
3. partition the changes into the smallest truthful completed-task or bridge-task boundaries
4. commit those boundaries immediately
5. update `session.json` to record any bridge-task recovery needed to restore queue integrity
6. resume the queue autonomously

Only stop for the user when the situation is catastrophic in the existing stop-condition sense.

## Bridge-Task Recovery

If two adjacent tasks became coupled in practice and cannot be truthfully separated after implementation has already begun, create a temporary bridge task in `session.json` that explains the dependency seam, commit that bridge task as its own proof boundary, and then continue.

Bridge tasks are allowed only to recover TACTIC integrity. They must be:

- minimal
- truthful
- written into `session.json` before commit
- used to restore one-task-one-commit discipline, not to excuse batching

## Forbidden Shortcut

Do not defer task-boundary commits with the intention of reconstructing them later.

If the run drifts into a multi-task dirty state, immediately enter TACTIC Integrity Recovery and restore truthful commit boundaries before continuing.

## Handle Blockers

In `autonomous` mode:

- resolve logic questions yourself unless they are catastrophic
- recover locally and resume when the problem is a non-catastrophic workflow or task-boundary issue
- stop only for catastrophic workspace-state anomalies, destructive contradictions, or environment breakage that makes further progress unsafe

In `regular` mode:

- ask known blocking questions before starting
- when a blocker appears mid-run, move that task and its dependents to the queue end
- continue all other runnable tasks
- when the queue reaches the end with blockers still unresolved, raise one consolidated blocker handoff instead of drip-feeding questions

When deferring work, update `blockedTaskIds`, `dependencyDeferrals`, and `recentNote` in `session.json`.

## Notify Progress

Use the global `notify` skill and the `notify` CLI for session visibility.

Default notification events:

- `start`
- after every completed task
- `block` when `regular` mode reaches the end of runnable work with unresolved blockers
- `finish`

Default message format:

```text
<Bot Name>: out of total X tasks - [D done / C current / R remaining]; last task <duration>, session <duration> - <optional short note>
```

Rules:

- Default bot name is `Codex`.
- Optional note must stay under one short sentence.
- `start` may render last task as `n/a`.
- `finish` must report the final counts truthfully.
- After every completed-task notification, the task should already be committed.

Resolve the bot name from `AXOLYNC_NOTIFY_BOT_NAME`, then `~/bin/notify-config.json`, then `Codex`.

## Stop Conditions

Stop immediately for catastrophic workspace-state failures.

Examples:

- repositories or directories suddenly disappear or contradict prior context
- persistent files look corrupted or unexpectedly rewritten in bulk
- the environment breaks in a way that makes follow-up writes unsafe

Do not self-heal or recreate damaged state during `TACTIC`. Report the problem clearly and preserve the state for inspection.
