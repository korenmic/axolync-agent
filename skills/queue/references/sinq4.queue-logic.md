# Sinq4 Queue Logic

## Core Rule

In `Sinq4`, the real queue is **not** "all unchecked tasks in all spec `tasks.md` files".

The real queue is the curated backlog artifact:

- `C:\Users\koren\src\Sinq4\axolync-builder\backlog\tasks.md`

When the user asks about:

- remaining queue
- queued tasks
- what is left
- what is in backlog

the default answer should come from that file first.

## Why This Matters

A raw scan of all unchecked spec tasks across repos produces many false positives:

- stale specs
- deprecated specs
- cancelled/suspended/superseded work
- old parent checklist rows left open even when meaningful child work is done
- historical planning artifacts that are no longer part of the active operator queue

That raw scan is useful only as a **diagnostic/backlog archaeology tool**, not as the primary queue answer.

## Active Queue Source Of Truth

Use:

- `axolync-builder/backlog/tasks.md`

Treat it as the operator-curated queue.

If a task is not represented there, do **not** assume it belongs in the active queue just because some spec file has unchecked boxes.

## Spec Tasks vs Queue

There are 3 different concepts that must stay separate:

1. `Seed`
- high-level idea / feature direction

2. `Spec trio`
- `.codex/specs/<spec>/requirements.md`
- `.codex/specs/<spec>/design.md`
- `.codex/specs/<spec>/tasks.md`
- these describe implementation work for a seed/spec

3. `Queue`
- the small curated set of work items the operator currently considers live
- in this workspace, that is the builder backlog file unless the user explicitly says otherwise

Do not collapse these into one thing.

## Archived / Hidden / Non-Queue Material

Per `axolync-builder/ai.md`:

- ignore archived material by default
- paths under `archived/` are out of normal planning/reporting scope
- directories with `.axolync-archive-policy.json` are out of normal planning/reporting scope
- `cancelled`, `suspended`, and `superseded` seeds are intentionally hidden from normal active inventory

Practical implication:

- do not surface old unchecked spec tasks unless the user explicitly asks for stale/history/archived work

## Correct Default Behavior For Agents

When the user asks "what remains?" or similar:

1. Check `axolync-builder/backlog/tasks.md`
2. Report unchecked items there
3. Give counts from that file
4. Only mention spec-task leftovers if:
- the user explicitly asks for all unchecked spec tasks
- or there is a reason to explain mismatch between queue and implementation state

## Secondary Cross-Check

A raw unchecked-task scan across `.codex/specs/**/tasks.md` may still be useful for:

- finding orphaned work that never got promoted into the queue
- finding umbrella rows left unchecked while subtasks were finished
- spotting queue/spec drift

But it should be framed as:

- "unchecked spec backlog"
- "orphaned/stale/planning residue"
- "non-queue items"

not as the active queue.

## Good Answer Shape

If asked for queue status, prefer answers like:

- "The real queue is `axolync-builder/backlog/tasks.md`."
- "There are `N` queued items remaining."
- "These are the queued items..."

If asked for broader leftovers, clarify the distinction:

- "Queue-wise, `N` remain."
- "There are also stale/orphaned unchecked spec tasks, but those are not part of the active queue."

## Known Failure Mode To Avoid

Bad behavior:

- recursively scan every `.codex/specs/*/tasks.md`
- list all unchecked items
- present them as "the remaining queue"

This was already proven wrong in this workspace.

## Better Merged Logic Proposal

For a future multi-agent merged queue model, use this precedence order:

1. Explicit user-named queue artifact
- if the user points to a backlog file, use that

2. Builder curated backlog
- `axolync-builder/backlog/tasks.md`

3. Explicit active/in-progress specs the user just worked on
- only if the user asks for "what we were just working on"

4. Raw unchecked spec scans
- only as non-authoritative fallback / audit output

## Current Human Meaning

In this workspace, "queue" means:

- the consciously curated next-work list
- not every historical unchecked planning checkbox

