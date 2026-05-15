# Queue Status Workspace Skill

## Summary

Create a `$queue-status` user skill in the agents repo for workspaces with an initiated task queue. The skill should report queue health without starting implementation: how many tasks exist, how many are done, how many remain ready/undone, and whether queued records are by-reference tasks or inline by-value tasks.

The goal is to make queue state auditable before a tactic run, after a tactic run, or during handoff between agents.

## Product Context

Axolync agents often use queued task execution across multiple Sinq workspaces. Today, an agent has to manually inspect queue files and referenced `tasks.md` files to understand what remains. That is error-prone, especially when queue records mix:

- references to spec `tasks.md` items
- hard-coded inline tasks inside the queue itself
- completed task records
- partially recognized or malformed records

`$queue-status` should give a concise status report and hand unrecognized records back to the AI so parser gaps can be classified manually and hardened later.

## Technical Constraints

- Implement under `axolync-agent/skills-user/queue-status`, not under `skills-workspace`.
- The skill may later be installed into a Codex user skill directory when explicitly requested, but this seed only defines the agents repo source.
- Use a script for deterministic queue discovery, parsing, counting, and classification.
- Prefer current workspace queue state as the default input.
- Support inspecting other local Sinq workspaces only as read-only evidence when explicitly requested.
- Do not start, modify, complete, or reorder queued tasks.
- Do not treat unrecognized records as successful parsing. Return them to the AI with enough raw context and parser reason to classify manually.
- Do not assume all queue records point to `tasks.md`. Inline by-value tasks are valid and must be counted distinctly.
- If no queue is found, fail gracefully with a clear "no initiated queue found" result, not a stack trace or hard error.

## Proposed Scope

1. Add a `queue-status` user skill with `$queue-status` as the primary invocation.
   - Place the skill source at `axolync-agent/skills-user/queue-status`.
   - Include invocation aliases if useful, but keep `$queue-status` as the canonical trigger.

2. Add a shared script that discovers and parses the current workspace queue.
   - Locate the active queue file or queue directory using the existing queue/tactic conventions.
   - Treat `<workspace-root>/.codex/local-task-queue.md` as the current established queue file convention when present.
   - Also detect legacy/alternate JSON queues such as `<workspace-root>/.codex/tmp/execution-queue.json`.
   - Prefer the Markdown queue when both Markdown and JSON queues exist, but report the lower-priority queue as an additional discovered queue artifact.
   - Treat a missing queue file as "no initiated queue" rather than as an error.
   - Parse JSON queues with top-level metadata and an `items` array.
   - Compute stable internal parser data as needed.
   - Emit a concise human-readable table or bullet summary for interactive use, without writing a second machine-readable status artifact by default.

3. Allow AI/context-assisted queue path fallback.
   - Script discovery should cover known conventions, hard-coded candidates, and lightweight local search where appropriate.
   - If script discovery does not find a queue, the skill workflow should allow the agent to use already-known context from the current conversation or workspace notes, such as a user-provided queue path.
   - Context-provided queue paths must still be validated as existing files before parsing.
   - The final report should state whether the queue path came from script discovery, explicit user/context fallback, or was not found.

4. Classify every queue record.
   - `by-reference`: the record points to a task in a specific `tasks.md` or equivalent task source.
   - `by-value`: the record contains the implementation task inline and does not depend on an external task source.
   - `unrecognized`: the script cannot safely classify the record.
   - Recognize current by-value source styles including `inline procedural queue task` and backticked labels such as `` `by-value review task` ``.
   - Recognize JSON reference-only queue records with `queue_id`, `status`, `source_file_path`, and `referenced_task_title`.
   - Treat JSON `notes`, `note`, `completedAt`, and `completed_at` as optional metadata, not classification requirements.

5. Count task state.
   - Total queued records.
   - Done/completed records.
   - Undone/ready records.
   - By-reference done/undone.
   - By-value done/undone.
   - Unrecognized records.

6. Resolve referenced task state when possible.
   - For `by-reference` records, inspect the referenced task source and compare queue-local done state with referenced task checkbox/status state.
   - Report disagreements instead of silently choosing one state.
   - Treat referenced task-source state as the preferred authority when the target is resolvable.
   - Canonicalize Windows Markdown-link paths that appear as `C:/...`, `/C:/...`, and `/c:/...`.
   - Support `.codex/specs/.../tasks.md`, `.kiro/specs/.../tasks.md`, and `backlog/tasks.md` references.
   - Report missing referenced task sources separately from unrecognized queue records.

7. Return parser gaps to the AI.
   - Include raw record text or a compact excerpt.
   - Include the parser reason.
   - Include the queue file path and record index.
   - Make it easy for the AI to classify gaps and propose parser hardening.

8. Provide cross-workspace diagnostic mode.
   - Allow explicit read-only inspection of Sinq, Sinq2, Sinq3, and Sinq4 queue states for parser validation.
   - Never modify those workspaces.

9. Avoid double-counting compacted history and summary sections.
   - Parse records under the active `## Queued Items` section.
   - Stop or switch mode at the next level-2 heading such as `## Most Recent Completed Items`.
   - If duplicate `Q-###` ids are observed, report them as history/summary duplication or corruption instead of silently counting them twice.

10. Normalize observed status labels.
   - Treat `done` and `completed` as completed states.
   - Treat `queued` as ready/undone.
   - Reserve explicit buckets for `in_progress`, `blocked`, and `skipped` even if they are not present in the current sample.
   - Preserve unknown status labels in the JSON output and the AI gap report.

11. Add deterministic fixture coverage from observed real queues.
   - Create copied or sanitized test fixtures derived from the observed Sinq, Sinq2, Sinq3, and Sinq4 queue files.
   - Do not make automated tests depend on live `C:/Users/.../Sinq*` paths existing.
   - Fixture coverage must prove parsing for Markdown local-task queues, JSON execution queues, status normalization, by-reference records, by-value records, missing referenced sources, and section-aware duplicate/history handling.
   - Keep live cross-workspace inspection as a manual diagnostic mode, separate from CI fixtures.

12. Add an optional verbose undone-task expansion.
   - Support a `verbose` argument for `$queue-status`.
   - When verbose is requested, include a short per-task summary for each enqueued undone record.
   - Summaries should include qid, normalized status, classification, and a compact task label or reference.
   - The verbose expansion remains human-readable only and must not persist a second machine-readable artifact.

13. Keep undone elaboration at the bottom of the report.
   - Move the `undone:` elaboration to the bottom of the output in all modes.
   - When `verbose` is supplied, place the per-task undone expansion adjacent to that bottom `undone:` section.
   - Keep top-level counts concise so the expanded undone list is not separated from the count it explains.

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

## Resolved Decisions

- Queue discovery should search `<workspace-root>/.codex/local-task-queue.md` first, then `<workspace-root>/.codex/tmp/execution-queue.json`, then allow explicit user/context-provided paths as fallback.
- Status normalization should treat `done` and `completed` as done, `queued` as ready, `in_progress` as active-undone, `blocked` as blocked-undone, `skipped` as skipped-not-done, and unknown labels as `unrecognized_status`.
- Blocked tasks should count in both `undone_total` and a separate `blocked` bucket.
- Queue-local status is authoritative for queue-status counts. Referenced `tasks.md` files may be inspected as optional evidence and drift diagnostics, but they must not cause un-enqueued tasks to affect queue-status output.
- A queue item id (`qid`) is the queue-local record identity, such as `Q-001` or `Q0001`. It identifies the queued record, not the referenced source task.
- `$queue-status` should output concise human-readable text only by default. It does not need to store or emit a second machine-data representation because the queue file itself is the machine-readable source.
- `$queue-status verbose` should expand only enqueued undone records with compact per-task summaries.
- The `undone:` elaboration should always appear at the bottom of the human report, and verbose undone-task details should be adjacent to that bottom section.
- Summary/history sections should be ignored for active counts, but scanned enough to warn about duplicate ids or suspicious overlap.

## Open Questions

- Should the eventual implementation include an optional debug flag for raw parser diagnostics, or should all parser gaps be summarized only in the human output?
