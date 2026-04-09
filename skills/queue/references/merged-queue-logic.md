# Merged Queue Logic

This note merges the local Axolync queue summaries into one reusable reference.

## Core Meaning

Queue means:

- a curated execution list
- local orchestration state
- append-only handoff memory

Queue does not mean:

- every unchecked task in every spec
- a replacement for backlog authority
- a replacement for spec `tasks.md`

## Source Precedence

When resolving "the queue", prefer this order:

1. an explicit user-named queue artifact
2. an already-established workspace-local queue artifact
3. a curated backlog file the workspace already treats as the live queue
4. the active spec `tasks.md` if the user is clearly working directly from that spec
5. raw unchecked-task scans only as audit/fallback output

For `C:\Users\koren\src\Sinq`, the established queue artifact is:

- `C:\Users\koren\src\Sinq\.codex\local-task-queue.md`

## Queue Item Philosophy

- local queue ids are orchestration ids only
- the queue is reference-based, not a second task authority
- every item should point back to the authoritative source markdown
- execution status belongs in the queue
- completion truth still belongs in the authoritative source file

## Queue And TACTIC

- adding to queue is not the same as executing the queue
- TACTIC runs tasks one at a time with verification and commit boundaries
- the queue provides local execution order and handoff memory
- the source backlog/spec file provides task wording and completion authority

## Wrong Default To Avoid

Do not treat a recursive scan of every unchecked spec task as the active queue.

That scan is only useful for:

- backlog archaeology
- spotting queue/spec drift
- finding orphaned unchecked work

## Cross-Agent Handoff Rule

When sharing a queued task across workspaces:

- do not share `Q-###` alone
- convert the queue item into a stable global task id first
- use the local `task-id` skill for that conversion
