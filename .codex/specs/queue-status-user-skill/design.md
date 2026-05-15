# Design

## Overview

`queue-status` is a read-only user skill backed by a deterministic parser script. It reports the health of a workspace queue without mutating queue files or executing tasks.

The design separates three responsibilities:

- Skill wrapper: explains invocation and safe workflow.
- Parser script: discovers, parses, classifies, and counts queue records.
- Fixture tests: lock the parser to observed queue formats without depending on live Sinq workspaces.

## Skill Location

The skill source will live at:

`axolync-agent/skills-user/queue-status`

The canonical invocation is `$queue-status`. The skill is sourced from the agents repo user-skill area. It is not automatically installed into `~/.codex/skills` by this spec.

## Script Location

Use a cross-platform Python script:

`axolync-agent/skills-user/queue-status/scripts/queue_status.py`

Python is appropriate because queue parsing is text/file oriented, the workspace already uses cross-platform scripts, and tests can invoke the same script without shell-specific parsing.

## Discovery Model

The script accepts:

- `--workspace-root <path>`: optional, defaults to the current working directory.
- `--queue-path <path>`: optional explicit path, used for context fallback or direct testing.
- `--diagnose-known-sinq-roots`: optional manual-only mode for local cross-workspace parser diagnostics.

Discovery order:

1. Explicit `--queue-path`, when supplied.
2. `<workspace-root>/.codex/local-task-queue.md`.
3. `<workspace-root>/.codex/tmp/execution-queue.json`.
4. No queue found.

If both Markdown and JSON queues exist, the Markdown queue is active and the JSON queue is reported as an additional discovered artifact.

The skill wrapper may pass a context-known path to `--queue-path` if script discovery fails and the user or conversation has named a queue file. The script validates that any explicit path exists before parsing.

## Queue Record Model

Internal parser records use this conceptual shape:

```text
qid: original queue item id, such as Q-001 or Q0001
format: markdown | json
classification: by-reference | by-value | unrecognized
status_raw: original status label
status_bucket: done | ready | active | blocked | skipped | unrecognized_status
task_label: queue task label or referenced task title
source_path: referenced source path when present
source_exists: true | false | null
section: active | history | unknown
warnings: list of human-readable parser warnings
```

The qid is queue-local identity only. It does not identify the referenced source task.

## Markdown Parser

The Markdown parser reads the active `## Queued Items` section and extracts records introduced by headings like:

```markdown
### Q-001
```

Supported fields:

- `- Status: ...`
- `- Source: ...`
- `- Task: ...`
- optional details or notes after the standard fields

The parser stops active counting at the next level-2 heading. It may scan later sections for duplicate qids and history-overlap warnings, but those sections do not affect active counts.

Source classification:

- Sources containing a Markdown link or path to `tasks.md` are `by-reference`.
- Sources matching inline styles such as `inline procedural queue task` or `` `by-value review task` `` are `by-value`.
- Other source shapes are `unrecognized`.

Markdown path normalization handles:

- `C:/...`
- `/C:/...`
- `/c:/...`
- ordinary absolute or relative paths where possible

## JSON Parser

The JSON parser supports Sinq3-style files such as:

`<workspace-root>/.codex/tmp/execution-queue.json`

Expected top-level shape:

```json
{
  "version": 1,
  "workspace_root": "...",
  "queue_kind": "reference_only_execution_queue",
  "items": []
}
```

Expected item fields:

- `queue_id`
- `status`
- `source_file_path`
- `referenced_task_title`

Optional metadata fields:

- `notes`
- `note`
- `completedAt`
- `completed_at`

JSON records with the expected fields are `by-reference`. Missing required fields produce unrecognized parser gaps.

## Status Normalization

Status normalization maps raw labels into buckets:

```text
done, completed -> done
queued -> ready
in_progress -> active
blocked -> blocked
skipped -> skipped
anything else -> unrecognized_status
```

Count rules:

- `done` contributes to done total.
- `ready`, `active`, and `blocked` contribute to undone total.
- `blocked` also contributes to the blocked bucket.
- `skipped` is separate and not done.
- `unrecognized_status` is surfaced as a parser gap.

## Reference Drift Diagnostics

Queue-local status is authoritative for queue-status counts.

Referenced `tasks.md` files are optional evidence only:

- Existing source files may be inspected for matching checklist task state.
- Missing source files are reported but do not fail parsing.
- Queue/source status disagreement is reported as drift.
- Un-enqueued tasks in referenced files never affect queue totals.

This prevents queue-status from becoming a recursive backlog scanner.

## Output

Default output is concise human text only.

Suggested sections:

- Queue source: discovered path and discovery method.
- Counts: total, done, undone, ready, active, blocked, skipped.
- Classification: by-reference, by-value, unrecognized.
- Reference diagnostics: missing sources and drift count.
- Parser gaps: compact list of unrecognized records/statuses.
- Additional discovered artifacts: lower-priority queue files found but not used.

The script may compute structured objects internally, but it does not persist a separate machine-readable queue-status file by default.

## Testing

Tests should live under:

`axolync-agent/skills-user/queue-status/tests`

Fixtures should live under:

`axolync-agent/skills-user/queue-status/tests/fixtures`

Fixture set:

- Sinq Markdown queue: many done records and one by-value review task.
- Sinq2 Markdown queue: done plus queued by-reference records.
- Sinq3 JSON queue: `items` array with `Q0001` ids and optional metadata fields.
- Sinq4 Markdown queue: `completed` statuses, inline procedural records, and a later history section with duplicate qids.

Fixtures must be sanitized and deterministic. They must not require live `C:/Users/.../Sinq*` paths.

## Self-Review Notes

- The design keeps queue-local status authoritative for queue-status counts, matching the resolved answer for Q4.
- The design does not emit or store JSON by default, matching the resolved answer for Q5.
- The design still permits internal structured data because parser code needs a normalized model, but that data is not a persisted output artifact.
- The design prevents un-enqueued source tasks from affecting counts.
- The design treats live Sinq cross-workspace inspection as manual diagnostics only, not CI dependency.
