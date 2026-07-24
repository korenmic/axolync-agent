---
name: deploy-workspace-skills
description: Expose the axolync-agent skills-workspace bucket to the current workspace for the running agent (Codex workspace junction or Claude workspace skills via claudify). Use when invoked as $deploy-workspace-skills or when the user asks to install or refresh the workspace skills.
---

# Deploy Workspace Skills

Expose `skills-workspace/` from the axolync-agent repo to the current workspace, for the agent that is currently running. The repo sources are the single source of truth; deployment never edits them.

## Resolve

1. Resolve the agent repo: the `axolync-agent` clone in the current workspace.
2. Resolve the workspace root: the top-level multi-repo workspace directory containing that clone.
3. Detect the running agent: a Codex session exposes the Codex shape; a Claude session exposes the Claude shape. Do not ask.

## Deploy

- Codex: follow the README junction rules — create the junction `<workspace>\.codex\skills` -> `<agent-repo>\skills-workspace` only when `<workspace>\.codex\skills` does not already exist. If it exists, inspect it and ask before replacing anything.
- Claude: run `python <agent-repo>/scripts/claudify.py`; it generates the Claude-form copies and installs the workspace-scope output into `<workspace>\.claude\skills` (its existing behavior), replacing existing same-name folders.

Rules:

- Workspace scope only: do not write into any user-global skills directory from this skill.
- Overwrite deployed Claude copies idempotently; the repo state wins.
- Do not edit the `skills-workspace/` sources.

## After

Newly exposed skills appear in `$`/`/` autocomplete only in sessions started after deployment; suggest a session restart/reload if discovery matters now. Report the exposure mechanism used (junction vs claudify install) and the workspace path.
