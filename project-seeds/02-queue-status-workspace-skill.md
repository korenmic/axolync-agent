# Queue Status Workspace Skill

## Summary

Create a `$queue-status` workspace skill for workspaces with an initiated task queue. The skill should report queue health without starting implementation: how many tasks exist, how many are done, how many remain ready/undone, and whether queued records are by-reference tasks or inline by-value tasks.

The goal is to make queue state auditable before a tactic run, after a tactic run, or during handoff between agents.

## Product Context

Axolync agents often use queued task execution across multiple Sinq workspaces. Today, an agent has to manually inspect queue files and referenced `tasks.md` files to understand what remains. That is error-prone, especially when queue records mix:

- references to spec `tasks.md` items
- hard-coded inline tasks inside the queue itself
- completed task records
- partially recognized or malformed records

`$queue-status` should give a concise status report and hand unrecognized records back to the AI so parser gaps can be classified manually and hardened later.

## Technical Constraints

- Implement as an agents repo workspace skill, not a global user skill.
- Use a script for deterministic queue discovery, parsing, counting, and classification.
- Prefer current workspace queue state as the default input.
- Support inspecting other local Sinq workspaces only as read-only evidence when explicitly requested.
- Do not start, modify, complete, or reorder queued tasks.
- Do not treat unrecognized records as successful parsing. Return them to the AI with enough raw context and parser reason to classify manually.
- Do not assume all queue records point to `tasks.md`. Inline by-value tasks are valid and must be counted distinctly.

## Proposed Scope

1. Add a `queue-status` skill with `$queue-status` as the primary invocation.

2. Add a shared script that discovers and parses the current workspace queue.
   - Locate the active queue file or queue directory using the existing queue/tactic conventions.
   - Treat `<workspace-root>/.codex/local-task-queue.md` as the current established queue file convention when present.
   - Also detect legacy/alternate JSON queues such as `<workspace-root>/.codex/tmp/execution-queue.json`.
   - Prefer the Markdown queue when both Markdown and JSON queues exist, but report the lower-priority queue as an additional discovered queue artifact.
   - Treat a missing queue file as "no initiated queue" rather than as an error.
   - Parse JSON queues with top-level metadata and an `items` array.
   - Emit a stable machine-readable JSON summary.
   - Emit a concise human-readable table or bullet summary for interactive use.

3. Classify every queue record.
   - `by-reference`: the record points to a task in a specific `tasks.md` or equivalent task source.
   - `by-value`: the record contains the implementation task inline and does not depend on an external task source.
   - `unrecognized`: the script cannot safely classify the record.
   - Recognize current by-value source styles including `inline procedural queue task` and backticked labels such as `` `by-value review task` ``.
   - Recognize JSON reference-only queue records with `queue_id`, `status`, `source_file_path`, and `referenced_task_title`.
   - Treat JSON `notes`, `note`, `completedAt`, and `completed_at` as optional metadata, not classification requirements.

4. Count task state.
   - Total queued records.
   - Done/completed records.
   - Undone/ready records.
   - By-reference done/undone.
   - By-value done/undone.
   - Unrecognized records.

5. Resolve referenced task state when possible.
   - For `by-reference` records, inspect the referenced task source and compare queue-local done state with referenced task checkbox/status state.
   - Report disagreements instead of silently choosing one state.
   - Treat referenced task-source state as the preferred authority when the target is resolvable.
   - Canonicalize Windows Markdown-link paths that appear as `C:/...`, `/C:/...`, and `/c:/...`.
   - Support `.codex/specs/.../tasks.md`, `.kiro/specs/.../tasks.md`, and `backlog/tasks.md` references.
   - Report missing referenced task sources separately from unrecognized queue records.

6. Return parser gaps to the AI.
   - Include raw record text or a compact excerpt.
   - Include the parser reason.
   - Include the queue file path and record index.
   - Make it easy for the AI to classify gaps and propose parser hardening.

7. Provide cross-workspace diagnostic mode.
   - Allow explicit read-only inspection of Sinq, Sinq2, Sinq3, and Sinq4 queue states for parser validation.
   - Never modify those workspaces.

8. Avoid double-counting compacted history and summary sections.
   - Parse records under the active `## Queued Items` section.
   - Stop or switch mode at the next level-2 heading such as `## Most Recent Completed Items`.
   - If duplicate `Q-###` ids are observed, report them as history/summary duplication or corruption instead of silently counting them twice.

9. Normalize observed status labels.
   - Treat `done` and `completed` as completed states.
   - Treat `queued` as ready/undone.
   - Reserve explicit buckets for `in_progress`, `blocked`, and `skipped` even if they are not present in the current sample.
   - Preserve unknown status labels in the JSON output and the AI gap report.

## Inspection Findings

The first inspection pass looked at workspace-local queues in:

- `C:/Users/koren/src/Sinq`
- `C:/Users/koren/src/Sinq2`
- `C:/Users/koren/src/Sinq3`
- `C:/Users/koren/src/Sinq4`

Observed queue state:

- `Sinq`, `Sinq2`, and `Sinq4` use `.codex/local-task-queue.md`.
- `Sinq3` had no `.codex/local-task-queue.md`, but has used `.codex/tmp/execution-queue.json`; the skill should detect and parse that alternate queue path.
- `Sinq` had hundreds of completed records, mostly by-reference, plus one by-value review task using source `` `by-value review task` ``.
- `Sinq2` had a mix of `done` and `queued` records, all by-reference, with references into `.kiro/specs/.../tasks.md` and `backlog/tasks.md`.
- `Sinq4` had completed records, by-reference records, and inline procedural records using `Source: inline procedural queue task`.
- `Sinq4` also contained duplicated `Q-169` and `Q-170` headings in a later `## Most Recent Completed Items` section, so the parser must be section-aware.

Observed path/reference shapes:

- Markdown links may use `C:/...`, `/C:/...`, or `/c:/...`.
- Referenced sources may no longer exist locally if the workspace has moved branches or compacted old temp work. This should be reported as missing reference evidence, not as a parser crash.
- Authoritative task files use checklist syntax like `- [x] 1. ...`, `- [ ] ...`, and backlog checklist entries without numeric task prefixes.

Observed Sinq3 JSON queue shape:

- Top-level keys include `version`, `workspace_root`, `queue_kind`, `append_only_order`, `next_queue_id`, `created_at`, `updated_at`, `notes`, and `items`.
- `queue_kind` was `reference_only_execution_queue`.
- Items use ids like `Q0001`, not Markdown ids like `Q-001`.
- Required item fields observed: `queue_id`, `status`, `source_file_path`, and `referenced_task_title`.
- Optional item fields observed: `notes`, `note`, `completedAt`, and `completed_at`.
- The inspected JSON queue had 120 items, all `done`, all by-reference, and 8 missing referenced task-source files. Missing sources should be visible in output but should not prevent status counting.

## Open Questions

- What is the exact active queue file/directory convention across current Sinq workspaces?
- What status markers should count as done, skipped, blocked, or ready?
- Should blocked tasks count as undone, or should they be reported in a separate blocked bucket?
- Should by-reference completion be authoritative from the queue record, the referenced `tasks.md`, or both with mismatch reporting?
- Should `$queue-status` output JSON by default, human text by default, or both?
- Should summary/history sections be parsed into a separate history bucket, or ignored except for duplicate/corruption warnings?
