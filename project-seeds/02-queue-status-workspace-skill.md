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
   - Emit a stable machine-readable JSON summary.
   - Emit a concise human-readable table or bullet summary for interactive use.

3. Classify every queue record.
   - `by-reference`: the record points to a task in a specific `tasks.md` or equivalent task source.
   - `by-value`: the record contains the implementation task inline and does not depend on an external task source.
   - `unrecognized`: the script cannot safely classify the record.

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

6. Return parser gaps to the AI.
   - Include raw record text or a compact excerpt.
   - Include the parser reason.
   - Include the queue file path and record index.
   - Make it easy for the AI to classify gaps and propose parser hardening.

7. Provide cross-workspace diagnostic mode.
   - Allow explicit read-only inspection of Sinq, Sinq2, Sinq3, and Sinq4 queue states for parser validation.
   - Never modify those workspaces.

## Open Questions

- What is the exact active queue file/directory convention across current Sinq workspaces?
- What status markers should count as done, skipped, blocked, or ready?
- Should blocked tasks count as undone, or should they be reported in a separate blocked bucket?
- Should by-reference completion be authoritative from the queue record, the referenced `tasks.md`, or both with mismatch reporting?
- Should `$queue-status` output JSON by default, human text by default, or both?
