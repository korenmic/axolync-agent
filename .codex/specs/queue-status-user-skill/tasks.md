# Tasks

- [x] 1. Create the `queue-status` user skill skeleton
  - Add `axolync-agent/skills-user/queue-status/SKILL.md`.
  - Document `$queue-status` as the canonical invocation.
  - State that the skill is read-only and must not execute or mutate queued tasks.
  - Reference the parser script and context-fallback behavior.

- [x] 2. Add deterministic queue-status parser script
  - Add `skills-user/queue-status/scripts/queue_status.py`.
  - Implement `--workspace-root` and `--queue-path`.
  - Discover queues in order: explicit path, `.codex/local-task-queue.md`, `.codex/tmp/execution-queue.json`.
  - Return a graceful no-queue-found human report when no queue exists.

- [ ] 3. Implement Markdown queue parsing
  - Parse only the active `## Queued Items` section for active counts.
  - Extract qid, status, source, task label, and optional detail text from `### Q-###` records.
  - Classify `tasks.md` sources as by-reference.
  - Classify inline source styles as by-value.
  - Scan later summary/history sections only for duplicate-overlap warnings.

- [ ] 4. Implement JSON queue parsing
  - Parse top-level JSON queues with an `items` array.
  - Support `queue_id`, `status`, `source_file_path`, and `referenced_task_title`.
  - Preserve optional metadata fields only as parser context.
  - Classify valid JSON records as by-reference.
  - Report missing required JSON fields as parser gaps.

- [ ] 5. Implement status normalization and counting
  - Normalize `done` and `completed` to done.
  - Normalize `queued` to ready-undone.
  - Normalize `in_progress` to active-undone.
  - Normalize `blocked` to blocked-undone and include it in the blocked bucket.
  - Normalize `skipped` to skipped-not-done.
  - Preserve unknown statuses as unrecognized status gaps.
  - Report total, done, undone, ready, active, blocked, skipped, by-reference, by-value, and unrecognized counts.

- [ ] 6. Implement reference diagnostics without changing count authority
  - Canonicalize Markdown-linked Windows paths including `C:/...`, `/C:/...`, and `/c:/...`.
  - Check whether referenced source files exist.
  - Report missing referenced sources without failing the run.
  - Optionally inspect resolvable `tasks.md` files for queue/source status drift.
  - Ensure un-enqueued tasks in referenced files never affect queue-status counts.

- [ ] 7. Implement human-readable output
  - Print the queue path and discovery method.
  - Print concise count summaries.
  - Print classification summaries.
  - Print missing-reference and drift diagnostics.
  - Print parser gaps with qid or record index, raw excerpt, and parser reason.
  - Do not write a persisted machine-readable queue-status output file by default.

- [ ] 8. Add sanitized parser fixtures from observed queues
  - Add a Sinq-style Markdown fixture with done by-reference records and a by-value review task.
  - Add a Sinq2-style Markdown fixture with done and queued by-reference records.
  - Add a Sinq3-style JSON fixture with `Q0001` ids, optional metadata fields, and missing-source examples.
  - Add a Sinq4-style Markdown fixture with completed statuses, inline procedural tasks, and duplicate qids in a history section.

- [ ] 9. Add parser regression tests
  - Test discovery priority and graceful no-queue behavior.
  - Test Markdown parsing and section-aware duplicate handling.
  - Test JSON parsing and optional metadata tolerance.
  - Test status normalization and count buckets.
  - Test by-reference vs by-value classification.
  - Test missing reference reporting.
  - Test that referenced but un-enqueued source tasks do not affect queue totals.

- [ ] 10. Self-review and document usage limits
  - Run the queue-status tests.
  - Run a manual local check against the current workspace queue if available.
  - Verify the skill docs clearly state read-only behavior, queue-local count authority, and context fallback.
  - Confirm the implementation stops after reporting status and does not start TACTIC or queue execution.
