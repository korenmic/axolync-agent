# Implement User Skill

## Summary

Create an `$implement` user skill in the agents repo. The skill is a thin operational wrapper for a standard implementation request:

> Implement all undone enqueued tasks using `$tactic`, `$notify` on each task's start, progress, and done; when all tasks finish, push the work to the agreed-upon branch. If no branch was agreed, push to `master` or the current branch according to context. Notify again when the push completes.

The goal is to avoid retyping the same implementation handoff every time a queue is ready to run.

## Product Context

Axolync work often follows this chain:

1. A seed is created.
2. `$s2s` turns it into requirements/design/tasks.
3. `$enqueue` adds the relevant undone tasks to the local queue.
4. `$implement` runs those undone queued tasks through the normal TACTIC discipline.

The implementation step needs to consistently:

- use `$tactic` rather than ad-hoc implementation
- use `$notify` for visibility
- handle each queued task as a real implementation unit
- finish by pushing the resulting committed work
- notify after the push has completed

## Technical Constraints

- Implement under `axolync-agent/skills-user/implement`.
- Do not implement `$implement` under `skills-workspace`; it is a reusable user skill.
- Canonical invocation is `$implement`.
- The skill should not replace `$tactic`; it should invoke and constrain it.
- The task source is the current workspace queue and only undone enqueued tasks.
- It should use the existing `$tactic` one-task-one-commit discipline.
- It should use `$notify` for task start, progress, done, and final push completion.
- It must push only after all runnable undone queued tasks are completed and committed.
- It must push to the branch agreed in the current conversation or dispatch context.
- If no branch was agreed, it should infer `master` or the current branch from context.
- If the branch choice is genuinely unsafe or ambiguous, ask for clarification before pushing.
- It must not silently create a new branch unless the user or context explicitly chose that branch.
- It should report blockers if `$tactic` cannot complete all runnable tasks.

## Proposed Scope

1. Add an `implement` user skill skeleton.
   - Place source at `axolync-agent/skills-user/implement`.
   - Document `$implement` as the canonical invocation.
   - Explain that it delegates implementation to `$tactic` and notifications to `$notify`.

2. Resolve the active queue.
   - Use the current workspace queue as the task source.
   - Select all undone enqueued tasks.
   - Do not scan unrelated specs/backlogs for extra work.
   - If no undone enqueued tasks exist, report that there is nothing to implement and do not push.

3. Run `$tactic`.
   - Invoke `$tactic` over all undone enqueued tasks.
   - Preserve TACTIC's one-task-one-commit rule.
   - Preserve TACTIC's blocker handling and integrity recovery rules.
   - Ensure task completion notifications happen only after the relevant task commit exists.

4. Use `$notify`.
   - Notify when implementation starts.
   - Notify on each task start/progress/done as supported by TACTIC/notify.
   - Notify when blockers stop the run.
   - Notify when all tasks finish.
   - Notify again after the final push completes.

5. Push after successful implementation.
   - Determine the target branch from explicit agreement first.
   - If no branch is agreed, infer from context whether `master` or the current branch is appropriate.
   - Fetch/rebase or otherwise update safely before pushing when needed.
   - Push only committed work.
   - If the push fails, report the exact blocker and do not claim completion.

6. Add usage and safety documentation.
   - Document that `$implement` is intentionally high-impact because it runs the queue and pushes.
   - Document that branch selection must be explicit or safely inferable.
   - Document that the skill should not run when the user only asks to enqueue, review, or inspect status.

## Resolved Decisions

- `$implement` is a thin workflow skill, not a new implementation engine.
- `$tactic` remains the authority for executing queued tasks.
- `$notify` remains the authority for progress notifications.
- The final push is part of `$implement` only after all queued tasks are completed and committed.
- Branch destination priority is: explicitly agreed branch, current context branch, then `master` when context indicates normal master work.
- `$implement` should mirror `$tactic` mode inference by default. Any additional arguments after the implementation target should be forwarded to `$tactic` rather than reinterpreted by `$implement`.
- `$implement` should warn when the worktree is not clean, but should let `$tactic` handle dirty or related state according to its original rules. `$implement` is a wrapper, not a TACTIC refactor or safeguard layer.

## Open Questions

- None.
