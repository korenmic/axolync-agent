# Tasks

- [x] 1. Create the `implement` user skill skeleton
  - Add `axolync-agent/skills-user/implement/SKILL.md`.
  - Keep the implementation in `skills-user`; do not create a workspace-skill variant.
  - Document `$implement` as the canonical invocation.
  - State that the skill is a wrapper over `$tactic` and `$notify`, not a replacement implementation engine.
  - Document that implementation should not start for review, enqueue-only, status-only, build, or planning requests.

- [ ] 2. Define task-source resolution and argument forwarding
  - Document the default source as current workspace undone enqueued tasks.
  - Document explicit implementation target handling.
  - Forward additional arguments to `$tactic` unchanged.
  - Let `$tactic` perform its normal mode inference when no mode is supplied.
  - Add guard wording that `$implement` must not scan unrelated specs/backlogs for extra work.

- [ ] 3. Add worktree warning behavior
  - Inspect relevant worktree state before invoking `$tactic`.
  - Warn when a relevant worktree is dirty.
  - Do not block solely because of dirty state.
  - Defer dirty-state handling, recovery, and catastrophic stop decisions to `$tactic`.

- [ ] 4. Specify notify integration
  - Notify when implementation starts.
  - Preserve TACTIC task start/progress/done notifications.
  - Notify on blocker stop.
  - Notify when all tasks finish.
  - Notify again after push completes.

- [ ] 5. Specify post-implementation push behavior
  - Push only after all runnable undone tasks are complete and committed.
  - Resolve branch from explicit agreement first, then current context, then `master` when context indicates normal master work.
  - Ask for clarification when branch inference is unsafe.
  - Do not silently create a branch.
  - Report exact push blockers without claiming completion.

- [ ] 6. Add wrapper regression tests or fixtures
  - Cover forwarding extra arguments to `$tactic`.
  - Cover no-undone-task no-op behavior.
  - Cover dirty worktree warning without wrapper-level blocking.
  - Cover branch selection priority.
  - Cover push failure reporting.
  - Cover wrapper notify boundary events.

- [ ] 7. Self-review and document usage limits
  - Verify the skill docs preserve TACTIC authority.
  - Verify the skill docs preserve notify authority.
  - Verify the docs describe the final push and push-complete notification.
  - Verify the docs avoid adding new implementation semantics beyond the wrapper.
