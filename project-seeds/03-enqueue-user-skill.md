# Enqueue User Skill

## Summary

Create a `$enqueue` user skill in the agents repo. The skill adds newly relevant undone tasks into the local execution queue, then reports queue health by running `$queue-status verbose` and manually stating how many undone tasks were added in the current enqueue session.

The skill is for queue population only. It must not implement tasks, mark tasks done, reorder existing queue records, or run TACTIC.

## Product Context

Axolync agents frequently create or update specs and then need to enqueue only the relevant unfinished work. Today this is done manually by editing `.codex/local-task-queue.md`, which is error-prone because the source can be:

- a newly created single spec
- a newly created group of specs
- one specific task added to an existing partially or fully completed spec
- multiple specific tasks added to an existing partially or fully completed spec
- a backlog `tasks.md` file
- a mix of by-reference tasks and occasional inline by-value queue items

`$enqueue` should standardize that handoff. It should not search every reachable spec or backlog for all possible unqueued undone work. It should enqueue only tasks that the agent can reasonably identify as related to the current conversation context: tasks the user names directly, tasks implied by "the tasks" after a seed/spec discussion, tasks just created by the current session, or approved task candidates still present in working context.

After enqueueing, it should immediately make the queue state visible by invoking `$queue-status verbose`, then add a short manual note such as: `Added 3 undone tasks in this enqueue session.`

## Technical Constraints

- Implement under `axolync-agent/skills-user/enqueue`, not under workspace-only skills.
- Treat the local queue file as the target queue, normally `<workspace-root>/.codex/local-task-queue.md`.
- Preserve existing queue records and append new records only.
- Generate the next queue id (`qid`) from the active queue, preserving the established local format such as `Q-481`.
- Queue only undone source tasks unless the user explicitly asks to enqueue completed work as an audit record.
- Do not enqueue unselected tasks from an existing spec when the user requested only one or a few specific task additions.
- Do not double-enqueue the same source task when it is already present in the queue.
- Support by-reference records for normal `tasks.md`/backlog tasks and by-value records only when the user provides inline task text that has no authoritative task file.
- Infer by-value tasks from context when the approved task text exists only in conversation/working memory and no source file owns it. Do not require the user to say `by-value`.
- If the workspace has no initiated Markdown queue, create `<workspace-root>/.codex/local-task-queue.md` using the established local queue format before appending.
- After enqueueing, run `$queue-status verbose`.
- After the queue-status verbose output, manually state how many undone tasks were added "now" in this enqueue session.
- If `$queue-status verbose` is unavailable or not yet implemented, the skill should fail clearly or fall back only with an explicit note that verbose support is missing.

## Proposed Scope

1. Add an `enqueue` user skill skeleton.
   - Place source at `axolync-agent/skills-user/enqueue`.
   - Canonical invocation is `$enqueue`.
   - Document that it mutates only the local queue file and does not run implementation.

2. Resolve the enqueue source.
   - Use conversation context to determine the intended task set; do not scan broadly for unrelated unqueued tasks.
   - Treat direct user references such as "these tasks", "the tasks", "that spec", "this seed", or explicit task numbers as scoped to the current discussion.
   - Accept a single spec task file.
   - Accept a group of spec task files.
   - Accept a specific task number or task title from an existing spec.
   - Accept multiple specific task numbers or titles from existing specs.
   - Accept backlog task files.
   - Accept inline by-value task text only when no authoritative task source exists.

3. Select only undone tasks.
   - Parse checklist state from source task files.
   - Queue unchecked tasks by default.
   - Ignore checked/done tasks unless explicitly requested.
   - For existing specs with new additions, enqueue only the requested new/undone task items rather than all historical unchecked work unless the user requests the whole spec.
   - Do not treat every unchecked task in every visible repo as in-scope merely because it is discoverable.

4. Prevent duplicate queue records.
   - Compare source path plus task label/title against existing queue records.
   - Prefer a stable source-task identity when available, such as source path plus task number/title. This source-task identity is separate from the queue id (`qid`), which identifies the queue record.
   - If a future task-id field exists in source task files, use it as the stronger duplicate key for by-reference tasks.
   - Preserve existing queue entries even when source task state changed.
   - Report skipped duplicates in the final response.

5. Append queue records.
   - If the queue file is missing, create it with the standard local queue header and an empty `## Queued Items` section.
   - Use the next qid after the current highest queue id.
   - Write records in the existing Markdown queue format:
     - heading `### Q-###`
     - status `queued`
     - source link or by-value source label
     - task label text
   - Keep append order deterministic.

6. Run queue status after enqueueing.
   - Invoke `$queue-status verbose` or the equivalent parser command once the queue file is updated.
   - Preserve queue-status as the source of truth for total/done/undone counts.
   - Add a manual enqueue-session note after the status output:
     - `Added N undone tasks in this enqueue session.`
     - Include duplicate/skipped count when nonzero.

7. Handle no-op enqueue sessions safely.
   - If all requested tasks are already queued or done, do not edit the queue.
   - Still report the reason and optionally run `$queue-status verbose` when useful.
   - Manual note should state `Added 0 undone tasks in this enqueue session.`

8. Handle context-only by-value tasks.
   - When the approved task exists only in current conversation context and no source file owns it, append a by-value queue record.
   - Use a clear source label such as `inline procedural queue task` or another established by-value source style.
   - Include enough task text for the future tactic runner to execute it without recovering the full original conversation.

9. Add regression fixtures and tests.
   - Fixture for a new spec with multiple unchecked tasks.
   - Fixture for an existing partially done spec with one newly requested task.
   - Fixture for multiple specs in one request.
   - Fixture for backlog tasks.
   - Fixture for duplicate prevention.
   - Fixture for qid continuation.
   - Fixture proving checked source tasks are not enqueued by default.
   - Fixture proving missing queue auto-creation.
   - Fixture proving context-only by-value tasks do not require the literal phrase `by-value`.

## Relationship To Queue Status

`$enqueue` depends on `$queue-status verbose` for final queue visibility. Queue-status remains read-only and authoritative for reporting. Enqueue owns only appending new queue records and reporting the count of records added in the current session.

The manual "added now" note is intentionally not derived from queue-status totals, because queue-status reports the whole queue. `$enqueue` must track the current session's append count itself and state it explicitly after queue-status output.

## Resolved Decisions

- No dry-run mode is required for the initial skill.
- Duplicate detection should skip the exact same source task when it is already queued. Use source path plus task number/title as the baseline identity; use a stronger source task-id if one exists later. This source task identity is distinct from `qid`, which is only the queue record id.
- By-value enqueueing does not require an explicit `by-value` phrase. Context can establish that a task is by-value when approved task text exists only in conversation/working memory and no source task file owns it.
- `$enqueue` should create `.codex/local-task-queue.md` when no queue exists.
- Duplicate matching should not use broad fuzzy matching. It should identify the same source task by source path plus task number/title, or by a stronger future task-id when available. It may normalize obvious Markdown wrappers, checklist markers, backticks, and whitespace, but it must not treat semantically similar wording as the same task unless the source identity proves it.

## Open Questions

- None.
