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
