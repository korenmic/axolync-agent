# Requirements

## Introduction

The queue-status user skill provides a read-only health report for an initiated local task queue. It must help an agent or human understand how many queued records exist, how many are done, how many remain, and how records are classified, without starting implementation or mutating queue state.

The source seed is `project-seeds/02-queue-status-workspace-skill.md`.

## Requirements

### Requirement 1: User Skill Placement And Invocation

**User Story:** As an agent maintainer, I want queue-status to live in the agents repo user-skill source area, so it can be installed or reused consistently without being tied to one workspace's `.codex/skills` junction.

#### Acceptance Criteria

1. WHEN the skill is created THEN the skill source SHALL live under `axolync-agent/skills-user/queue-status`.
2. WHEN the skill is invoked THEN `$queue-status` SHALL be the canonical invocation.
3. WHEN the skill runs THEN it SHALL inspect queue state only and SHALL NOT start, reorder, complete, or modify queued tasks.
4. WHEN the skill cannot locate a queue THEN it SHALL report a clear "no initiated queue found" result instead of throwing an unhandled error.

### Requirement 2: Queue Discovery

**User Story:** As an agent using the skill, I want queue discovery to find the current queue using known conventions and context fallback, so queue status works across existing Sinq queue formats.

#### Acceptance Criteria

1. WHEN no explicit path is supplied THEN the discovery script SHALL first check `<workspace-root>/.codex/local-task-queue.md`.
2. WHEN the Markdown queue is not found THEN the discovery script SHALL check `<workspace-root>/.codex/tmp/execution-queue.json`.
3. WHEN both Markdown and JSON queues exist THEN the skill SHALL prefer the Markdown queue for active status and SHALL report the JSON queue as an additional discovered artifact.
4. WHEN script discovery fails but the current conversation or user provides a queue path THEN the skill workflow SHALL allow that path as a context fallback after validating that it exists.
5. WHEN the final report is shown THEN it SHALL state whether the queue path came from script discovery, context fallback, or no queue was found.

### Requirement 3: Markdown Queue Parsing

**User Story:** As an agent inspecting existing Markdown queues, I want the parser to understand current queue record structure without double-counting history sections.

#### Acceptance Criteria

1. WHEN parsing a Markdown queue THEN the parser SHALL parse records under the active `## Queued Items` section.
2. WHEN parsing reaches another level-2 section such as `## Most Recent Completed Items` THEN active queue counting SHALL stop or switch out of active-count mode.
3. WHEN Markdown records use ids like `Q-001` THEN the parser SHALL treat the id as the queue item id, or `qid`.
4. WHEN a record has a `Source` line that links to `tasks.md` THEN the parser SHALL classify it as `by-reference`.
5. WHEN a record has a source such as `inline procedural queue task` or `` `by-value review task` `` THEN the parser SHALL classify it as `by-value`.
6. WHEN duplicate qids appear outside the active queue section THEN the parser SHALL warn about duplicate or history overlap without counting them twice.

### Requirement 4: JSON Queue Parsing

**User Story:** As an agent inspecting JSON queues, I want the parser to handle Sinq3-style reference-only queues without requiring a Markdown queue file.

#### Acceptance Criteria

1. WHEN parsing a JSON queue THEN the parser SHALL support a top-level object with an `items` array.
2. WHEN JSON records include `queue_id`, `status`, `source_file_path`, and `referenced_task_title` THEN the parser SHALL classify them as `by-reference`.
3. WHEN JSON records include optional fields such as `notes`, `note`, `completedAt`, or `completed_at` THEN the parser SHALL preserve them only as optional context and SHALL NOT require them for classification.
4. WHEN JSON qids use forms like `Q0001` THEN the parser SHALL preserve the original qid format.
5. WHEN a JSON queue has no undone records THEN the skill SHALL still report total and completed counts.

### Requirement 5: Status Normalization And Counts

**User Story:** As an agent deciding what remains in a queue, I want consistent counts across different status labels.

#### Acceptance Criteria

1. WHEN a queue record status is `done` or `completed` THEN the parser SHALL count it as done.
2. WHEN a queue record status is `queued` THEN the parser SHALL count it as ready and undone.
3. WHEN a queue record status is `in_progress` THEN the parser SHALL count it as active and undone.
4. WHEN a queue record status is `blocked` THEN the parser SHALL count it in both `undone_total` and a separate `blocked` bucket.
5. WHEN a queue record status is `skipped` THEN the parser SHALL count it as skipped and not done.
6. WHEN a queue record status is unknown THEN the parser SHALL preserve it under `unrecognized_status` and include it in parser gaps.
7. WHEN producing totals THEN the skill SHALL report total records, done records, undone records, by-reference records, by-value records, blocked records, skipped records, and unrecognized records.

### Requirement 6: Queue Authority And Reference Drift

**User Story:** As an agent reviewing queue health, I want queue status to reflect only enqueued records while still surfacing reference drift.

#### Acceptance Criteria

1. WHEN a by-reference queue record points to a `tasks.md` file THEN the queue record status SHALL remain authoritative for queue-status counts.
2. WHEN a referenced `tasks.md` file has unchecked tasks not present in the queue THEN those un-enqueued tasks SHALL NOT affect queue-status counts.
3. WHEN a referenced source file exists THEN the parser MAY inspect it for optional drift evidence.
4. WHEN queue-local status disagrees with referenced task checkbox state THEN the report SHALL surface a drift warning without changing the queue count.
5. WHEN a referenced source file is missing THEN the report SHALL show missing reference evidence without failing the whole queue-status run.
6. WHEN parsing Windows paths from Markdown links THEN the parser SHALL canonicalize `C:/...`, `/C:/...`, and `/c:/...`.

### Requirement 7: Human Output And Parser Gaps

**User Story:** As a user reading the skill response, I want a concise human report that includes unresolved parser gaps without generating redundant machine data.

#### Acceptance Criteria

1. WHEN the skill completes THEN it SHALL output concise human-readable text by default.
2. WHEN queue records are unrecognized THEN the output SHALL include the qid or record index, source path or queue path, raw excerpt, and parser reason.
3. WHEN status labels are unknown THEN the output SHALL include the unknown labels and affected qids.
4. WHEN references are missing THEN the output SHALL include a compact missing-reference count and representative qids.
5. WHEN the script internally computes structured data THEN the skill SHALL NOT persist a second machine-readable queue-status artifact by default.

### Requirement 8: Deterministic Testing

**User Story:** As a maintainer, I want tests based on real observed queue shapes, so future parser changes do not regress across existing queue variants.

#### Acceptance Criteria

1. WHEN tests are added THEN they SHALL use copied or sanitized fixtures derived from observed Sinq, Sinq2, Sinq3, and Sinq4 queue files.
2. WHEN tests run in CI THEN they SHALL NOT depend on live `C:/Users/.../Sinq*` paths existing.
3. WHEN fixture tests run THEN they SHALL cover Markdown queues, JSON queues, status normalization, by-reference records, by-value records, missing referenced sources, and section-aware duplicate/history handling.
4. WHEN live cross-workspace inspection is needed THEN it SHALL remain a manual diagnostic mode separate from deterministic CI fixtures.

### Requirement 9: Verbose Undone Output

**User Story:** As a user inspecting a queue with remaining work, I want an optional verbose mode that summarizes each undone queued task next to the undone count, so I can see what remains without manually opening the queue file.

#### Acceptance Criteria

1. WHEN queue-status is invoked with a `verbose` argument THEN the skill SHALL include a compact per-task summary for each enqueued undone queue record.
2. WHEN verbose undone summaries are printed THEN each summary SHALL include the qid, normalized status, classification, and a compact task label or reference.
3. WHEN queue-status prints human output in any mode THEN the `undone:` elaboration SHALL appear at the bottom of the report.
4. WHEN verbose mode is active THEN the expanded undone-task list SHALL be adjacent to the bottom `undone:` elaboration.
5. WHEN verbose mode is inactive THEN queue-status SHALL keep the report concise and SHALL NOT print the per-task undone expansion.
6. WHEN verbose mode runs THEN it SHALL remain read-only and SHALL NOT persist a second machine-readable queue-status artifact.
