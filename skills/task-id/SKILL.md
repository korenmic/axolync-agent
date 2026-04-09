---
name: task-id
description: Create and resolve Axolync global task ids from queued items or authoritative markdown task files. Use when a task must be handed to another agent, referenced across workspaces, or converted between a local queue id and a stable source-backed id.
---

# Task Id

Use this skill to make task references portable across Axolync workspaces.

## Id Forms

Every task id has two forms:

1. Human-readable

- `htid1:repo::relative/source/path.md::task_index`

2. Packed

- `atid1:<payload>`

`htid1` means `Human Task ID v1`.
`atid1` means `Axolync Task ID v1`.

The packed form is a reversible compact encoding of the human-readable form. It is for copy-paste transport, not as the source of truth.

## Preferred Script

Use:

- [scripts/task_id.mjs](./scripts/task_id.mjs)

## Common Commands

From a queue item:

```powershell
node skills/task-id/scripts/task_id.mjs from-queue Q-129 --workspace-root C:\Users\koren\src\Sinq --format blob
```

From a source task file and index:

```powershell
node skills/task-id/scripts/task_id.mjs from-source C:\Users\koren\src\Sinq\axolync-browser\backlog\tasks.md 186 --workspace-root C:\Users\koren\src\Sinq --format blob
```

Decode a packed id:

```powershell
node skills/task-id/scripts/task_id.mjs decode "atid1:..." --format json
```

Resolve any human-readable or packed id back to file + task text:

```powershell
node skills/task-id/scripts/task_id.mjs resolve "htid1:axolync-browser::backlog/tasks.md::24" --workspace-root C:\Users\koren\src\Sinq --format blob
node skills/task-id/scripts/task_id.mjs resolve "atid1:..." --workspace-root C:\Users\koren\src\Sinq --format blob
```

## Resolution Rules

- If the source markdown task has a numeric prefix like `14.`, that numeric prefix is the task index.
- If the source markdown task is not numbered, count checklist tasks before it in the same file, starting at `1`.
- Use the authoritative markdown file to recover the task text.
- Treat queue `Q-###` ids as local-only and convert them before handoff.

## Output Rule

For chat handoff, emit one fenced `text` block per task and include:

- canonical id
- packed id
- authoritative absolute source path
- task text

Do not merge multiple tasks into one block.
