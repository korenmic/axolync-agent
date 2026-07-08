# 189 - P1 Refresh Workspace Skills Skill

## Summary

Create a workspace skill that updates the current workspace's Codex skill availability from the latest `axolync-agent` master, then makes those workspace skills available to the active Codex workspace/session as much as the local runtime permits.

Recommended skill name:
- `refresh-workspace-skills`

Recommended shortcut:
- `$refresh-workspace-skills`

Alternative names considered:
- `sync-workspace-skills`
- `reload-workspace-skills`
- `apply-agent-skills`

## Product Context

Axolync workspace skills live in the `axolync-agent` repo, but individual Codex workspaces and current Codex sessions can drift behind latest `origin/master`. The user wants a shortcut that does the maintenance work needed to pull latest agent skills and apply them to the current workspace without installing workspace skills into the user's Codex homedir.

This is different from user-profile skill installation. It should operate on workspace skill exposure and current workspace readiness only.

## Technical Constraints

- Implement as a workspace skill in `axolync-agent/skills-workspace/refresh-workspace-skills`.
- Pull latest `origin/master` for `axolync-agent`.
- Do not install workspace skills into `~/.codex/skills`.
- Do not mutate unrelated user-profile skills.
- Prefer linking or copying workspace skill definitions according to the existing agent bootstrap convention.
- Detect dirty `axolync-agent` state before pulling and stop/report instead of overwriting local work.
- Detect whether the current workspace has a `.codex/skills` link/copy that points at or mirrors `axolync-agent/skills-workspace`.
- Repair stale or missing workspace skill exposure when safe.
- Explain when a current Codex thread cannot dynamically reload newly added skill metadata without a new session.
- When runtime reload is impossible, report the exact restart/new-session requirement instead of pretending the skill is active.
- Respect RTK command rules when active.

## Proposed Skill Behavior

1. Inspect `axolync-agent`.
   - Verify the repo exists.
   - Verify worktree cleanliness.
   - Pull latest `master` from origin using fast-forward only.

2. Inspect current workspace skill exposure.
   - Locate current workspace root.
   - Inspect `<workspace>/.codex/skills`.
   - Identify whether it is a link, copy, missing folder, or stale folder.

3. Apply workspace skills safely.
   - Prefer the existing bootstrap convention used by Axolync workspaces.
   - Do not touch `~/.codex/skills`.
   - Do not overwrite dirty local workspace skill files without reporting first.

4. Verify.
   - List workspace skills now visible from the filesystem.
   - Compare against `axolync-agent/skills-workspace`.
   - Report missing or extra workspace skills.

5. Session reload caveat.
   - If the active Codex runtime cannot dynamically reload the skill list, state that a new Codex session is needed.
   - If a supported runtime refresh command exists later, the skill may use it.

## Required Tests / Validation

- Validate skill frontmatter and naming.
- Add a dry-run mode if implementation needs filesystem repair logic.
- Test detection of clean linked workspace skills.
- Test detection of missing workspace skill root.
- Test dirty-state refusal before destructive repair.
- Test that user homedir skills are not modified.

## Open Questions

None.

