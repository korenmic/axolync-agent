---
name: refresh-workspace-skills
description: "Pull latest axolync-agent master and apply or verify workspace skill exposure for the current workspace without installing skills into the user Codex homedir. Use when invoked as $refresh-workspace-skills or when workspace skills, autocomplete, or runtime availability appear stale."
---

# Refresh Workspace Skills

Use this workspace skill when the user wants the current workspace to pick up the latest workspace skills tracked in `axolync-agent`.

This skill is workspace-only. Do not install, copy, or update skills in `~/.codex/skills`.

## Shortcut

Use `$refresh-workspace-skills` as the canonical shortcut.

## Safe Agent Repo Update

Locate the `axolync-agent` repository before changing anything. Prefer the known sibling path when available, but verify it is a Git worktree before using it.

Before pulling, inspect the repo state. If `axolync-agent` has uncommitted changes, untracked skill files, merge conflicts, or an in-progress operation, stop and report the exact blocker. Do not rename, delete, stash, reset, or overwrite dirty files.

When the repo is clean, update only with a fast-forward pull from `origin/master`. If the pull cannot fast-forward, stop and report the current branch, local HEAD, upstream HEAD, and Git error.

Do not keep working from a stale local skill tree after an update failure. Report that workspace refresh could not be proven current.

## Workspace Skill Exposure

Locate the current workspace root, then inspect `<workspace>/.codex/skills` and compare it with `axolync-agent/skills-workspace`.

Report workspace skills that are:

- missing from the workspace exposure path
- stale compared with `axolync-agent/skills-workspace`
- copied when the workspace convention expects a link
- linked to the wrong source
- dirty or locally modified inside the workspace exposure path

If the workspace has an existing Axolync bootstrap convention for exposing workspace skills, use that convention for safe repair. Do not invent a new layout unless the existing convention is absent and the user explicitly approves the fallback.

Never overwrite dirty workspace skill files. If a repair would replace modified files, stop and report the exact files and the intended source path.

## User Homedir And Runtime Reload Boundaries

Do not mutate `~/.codex/skills` or any user-profile skill install when refreshing workspace skills. This workflow is only for workspace skill exposure.

After update or repair, compare the workspace-visible skill names against `axolync-agent/skills-workspace` and report any remaining mismatch.

If the current Codex session cannot dynamically reload newly exposed workspace skills, say that a new Codex session or workspace reload is required. Do not claim a skill is available in the active session unless it appears in the active skills list or the user confirms reload.

If a skill exists on disk but is not active in the current session, report both facts separately.
