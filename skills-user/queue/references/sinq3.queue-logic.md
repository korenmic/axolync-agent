# Sinq3 Queue Logic

This note summarizes the queueing logic currently used in the `C:\Users\koren\src\Sinq3` workspace.

It is a summary for agent consumption, not the authoritative queue itself.

## Authority

- The authoritative local queue file is:
  - `C:\Users\koren\src\Sinq3\.codex\tmp\execution-queue.json`
- The queue is intentionally local-only.
- It must live outside tracked repos to avoid repo churn.
- The queue must never become a second source of truth for tasks.

## Core Principles

1. The queue is reference-based, not copy-based.
2. Queue order is append-only unless the user explicitly asks to reorder.
3. Each queue item points back to the authoritative task source file.
4. The task source file remains the only real authority for task wording and completion.
5. The queue is for execution state, ordering, and local orchestration.

## What Can Be Queued

- An individual backlog task
- An individual task from a spec `tasks.md`
- A fresh spec whose tasks are all still unchecked

In practice, the queue has mainly been used for spec task items from:
- `axolync-addon-whisper/.codex/specs/.../tasks.md`

## Required Queue Item Fields

Each item should include:

- `queue_id`
  - Stable local id such as `Q0001`
- `status`
  - One of: `queued`, `in_progress`, `blocked`, `done`, `skipped`
- `source_file_path`
  - Absolute path to the authoritative source file
- `referenced_task_title`
  - Exact task title snapshot for readability
- `notes`
  - Optional short execution note

Queue-level metadata currently includes:

- `version`
- `workspace_root`
- `queue_kind`
- `append_only_order`
- `next_queue_id`
- `created_at`
- `updated_at`
- `notes`

## Status Semantics

- `queued`
  - Not started yet
- `in_progress`
  - Currently being worked
- `blocked`
  - Catastrophically blocked for now; queue execution should continue past it
- `done`
  - Implemented and verified enough to close the queue item
- `skipped`
  - Intentionally not executed

## Add Logic

When adding items:

1. First check whether an existing local queue file already exists.
2. Reuse it if appropriate.
3. Append new items only.
4. Do not renumber or reshuffle old items just because new prerequisites exist.
5. Add items by reference only.

Good behavior:

- copy the exact task title as a snapshot label
- store the source file path
- keep notes short and execution-oriented

Bad behavior:

- pasting the full task body into the queue
- editing the queue label and then treating that edited text as task authority
- using the queue as a substitute for checking off the real `tasks.md`

## Refresh Logic

If a referenced task changes upstream:

- prefer refreshing the queue label from the authoritative source
- do not treat stale queue text as authoritative

This means the queue should be easy to repair after spec edits.

## Play Logic

When asked to "play the queue":

1. Execute all items still in `queued`
2. Update the queue file after each meaningful state change
3. Resolve non-catastrophic blockers autonomously
4. If an item is catastrophically blocked:
   - mark it `blocked`
   - record a short reason in `notes`
   - continue to the next unblocked item
5. Reorder pragmatically by prerequisites only if necessary for real execution
6. Keep the queue file truthful about the real execution order and state

Important nuance:

- The queue is append-only by default
- Execution order may still be adapted if prerequisites require it
- If that happens, the queue file should reflect reality through status and notes rather than pretending the original order was strictly executable

## Execution Style Used So Far

The queue has been used together with a TACTIC-style workflow:

1. take one explicit task at a time
2. implement code
3. add or update tests
4. verify
5. fix if needed
6. mark the authoritative task complete
7. commit task-scoped work
8. move on

The queue is not the TACTIC authority.
It is only the local orchestration layer over the real spec/backlog authority.

## Relationship To Specs

For spec-driven work:

- queue items should point to the spec `tasks.md`
- task completion must be reflected in the real `tasks.md`
- if the seed/spec is effectively completed, related seed/spec metadata may also be updated

The queue helps coordinate execution, but the spec files remain the product/planning record.

## Example Of Current Real Usage

The current queue file contains completed item ranges like:

- `Q0001` to `Q0008`
  - Whisper Seed 05 tasks
- `Q0009` to `Q0014`
  - Whisper Seed 04 tasks
- `Q0015` to `Q0020`
  - Whisper Seed 06 tasks

Notes were used to capture short truthful summaries of what each completed task actually changed.

## Recommended Mergeable Ideas

If another agent is trying to improve this queue logic, the current best parts worth preserving are:

- local-only storage under `.codex/`
- reference-only task links
- append-only ids
- status truth over cosmetic neatness
- queue updates during execution, not only at the end
- queue notes as lightweight execution memory

Likely areas for improvement:

- better prerequisite modeling without violating append-only order
- a clearer distinction between "original requested order" and "actual execution order"
- automatic label refresh from source files
- optional provenance fields for repo/spec/task lineage
