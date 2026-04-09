# Sinq1 Queue Logic

This note merges the current queue behavior used across the Sinq workspace family into one practical rule set for agents.

It is a helper summary, not the authoritative queue itself.

## Core Meaning

In this workspace family, a queue is a **curated local execution list**, not "all unchecked tasks everywhere."

The queue exists to track:

- what was intentionally promoted for execution
- local ordering
- execution status
- lightweight handoff memory

The queue does **not** replace:

- seed docs
- spec trios
- `tasks.md`
- backlog files

Those remain the planning authority.

## Source Precedence

When an agent needs to answer "what is the queue?" or "add to queue", use this precedence:

1. An explicit user-named queue artifact
2. An already-established workspace local queue artifact
3. A curated backlog file the workspace already treats as the live queue
4. An explicit spec `tasks.md` the user is actively working from
5. Raw unchecked-task scans only as a fallback or audit tool

Important rule:

- never treat a recursive scan of every unchecked spec task as the default active queue unless the user explicitly asks for that

## Current Sinq Workspace

For `C:\Users\koren\src\Sinq`, the established local queue artifact is:

- `C:\Users\koren\src\Sinq\.codex\local-task-queue.md`

So when the user says "add to queue" in this workspace, the default meaning is:

- append new local queue entries into that markdown file

## What "Add To Queue" Means

Adding to queue means:

1. Find the current authoritative task source
   - usually a spec `tasks.md`
   - sometimes a backlog file
2. Reuse the existing queue artifact if it already exists
3. Append new items only
4. Assign the next contiguous local queue id such as `Q-067`
5. Set status to `queued`
6. Store the authoritative source file path
7. Copy only the task title/label as a readability snapshot
8. Do **not** copy the whole task body into the queue
9. Do **not** mark the source task complete
10. Do **not** start implementation unless the user asked for execution too

## Queue Item Shape

For the current markdown queue style, each item should include:

- local queue id
- status
- source path
- task title snapshot

Example shape:

```md
### Q-067
- Status: `queued`
- Source: [tasks.md](/abs/path/to/tasks.md)
- Task: `1. Example task title`
```

## Status Semantics

- `queued`
  - intentionally promoted into the queue, not started
- `in_progress`
  - currently being worked
- `blocked`
  - cannot proceed right now, but should remain visible
- `done`
  - implemented and verified enough to close the queue item
- `skipped`
  - intentionally not executed

## Append-Only Rule

Queue ids and queue order are append-only by default.

That means:

- do not renumber older entries
- do not reshuffle existing entries just because a new prerequisite appears
- if execution later happens in a different order, reflect that in status/notes rather than pretending the queue never changed reality

## Reference-Only Rule

The queue is an orchestration layer, not the source of truth.

So:

- task wording authority stays in the source `tasks.md` or backlog file
- if the source wording later changes, the queue label may be refreshed
- completion must still be reflected in the authoritative task source, not only in the queue

## Subset Queueing

If the user asks for only some tasks, append only those tasks.

Examples:

- "add tasks 1-6 to the queue"
- "add all tasks except 7"
- "add this single backlog item to the queue"

Do not silently add neighboring tasks the user did not ask for.

## Relationship To Execution

Adding to queue and playing the queue are different actions.

- "add to queue"
  - append entries only
  - no implementation
- "play the queue" / TACTIC execution
  - execute queued items one at a time
  - update status truthfully during execution

Execution may reorder pragmatically if prerequisites require it, but that is an execution concern, not an add-to-queue concern.

## Seed / Spec / Queue Distinction

Keep these separate:

1. Seed
   - feature direction / product framing
2. Spec trio
   - requirements / design / tasks
3. Queue
   - local curated execution list

Agents should not collapse them into one concept.

## Short Definition

For Sinq-family workspaces, "add to queue" means:

- append the requested authoritative task items by reference into the established local queue artifact
- assign the next local `Q-*` ids
- mark them `queued`
- preserve append order
- do not start implementation
- do not treat the queue as task authority
