---
name: queue
description: Resolve, inspect, update, and hand off Axolync queued tasks from the workspace root queue file, including emitting stable global task ids through the local task-id skill. Use when the user asks what is queued, wants enqueue/dequeue/reorder help, or needs copy-pasteable task handoff blobs for another agent.
---

# Queue

Use this skill for the Axolync workspace queue at:

- `<workspaceRoot>/.codex/local-task-queue.md`

## Core Rules

- Treat `Q-###` ids as local queue row ids only.
- Do not use `Q-###` alone for cross-workspace handoff.
- For agent handoff, emit one standalone plain-text blob per task.
- Use the local `task-id` skill to convert queue items into stable global task ids.

## Queue Logic References

This skill is Axolync-local and also carries forward the earlier queue-logic notes collected under:

- `C:\Users\koren\tmp\queue_logic\`

Use the merged summary in:

- [references/merged-queue-logic.md](./references/merged-queue-logic.md)

The raw per-agent notes are also preserved in the same folder for review.

## Global Task Id Requirement

Every queued task handoff should include:

- human-readable id
- packed id
- authoritative source path
- task text

Human-readable id format:

- `htid1:repo::relative/source/path.md::task_index`

Examples:

- `htid1:axolync-browser::backlog/tasks.md::186`
- `htid1:axolync-builder::.codex/specs/inspect-profiles-for-tests-and-work-queues/tasks.md::14`

Packed id format:

- `atid1:<payload>`

Where:

- `htid1` means `Human Task ID v1`
- `atid1` means `Axolync Task ID v1`
- `<payload>` is the reversible compact encoding of the human-readable id body

## Task Index Rule

When the source markdown task already carries a numeric prefix such as `14.`, use that number as the task index.

When the source markdown task is not explicitly numbered, compute the task index by counting checklist tasks before it in the same file, starting at `1`.

## Preferred Tooling

Use:

- [scripts/task_id.mjs](./scripts/task_id.mjs)

Preferred commands:

```powershell
node skills/task-id/scripts/task_id.mjs from-queue Q-129 --workspace-root C:\Users\koren\src\Sinq --format blob
node skills/task-id/scripts/task_id.mjs resolve "atid1:..." --workspace-root C:\Users\koren\src\Sinq --format json
```

## Handoff Output Shape

When preparing a handoff for another agent, emit one fenced `text` block per task. Do not combine multiple tasks into one blob.

The blob should contain:

- `TASK-ID-HTID1: <human-readable id>`
- `TASK-ID-ATID1: <packed>`
- `SOURCE: <absolute path>`
- `TEXT: <task text>`

## Queue Editing

When enqueueing or dequeueing:

- keep the root queue file as the execution list
- keep the authoritative backlog/spec file as the source of truth for the task text
- do not silently rewrite task meaning while moving queue entries around
