---
name: deploy-userspace-skills
description: Deploy the axolync-agent skills-user bucket into the running agent's userspace skills directory (Codex user skills dir or Claude user skills dir). Use when invoked as $deploy-userspace-skills or when the user asks to install or refresh the userspace skills for the current agent.
---

# Deploy Userspace Skills

Deploy the whole `skills-user/` bucket from the axolync-agent repo into the userspace skills directory of the agent that is currently running. The repo sources are the single source of truth; deployment never edits them.

## Resolve

1. Resolve the agent repo: the `axolync-agent` clone in the current workspace (or the repo this skill file lives in).
2. Detect the running agent: a Codex session deploys the Codex shape; a Claude session deploys the Claude shape. Do not ask.
3. Resolve the target:
   - Codex: the user Codex skills directory (normally `~/.codex/skills`).
   - Claude: the user Claude skills directory (normally `~/.claude/skills`).

## Deploy

- Codex: for each folder in `<agent-repo>/skills-user/`, copy it into the target, replacing any existing folder of the same name.
- Claude: run `python <agent-repo>/scripts/claudify.py` to generate the Claude-form copies, then install the generated user-scope skill folders into the target, replacing existing same-name folders.

Rules:

- Deploy the WHOLE bucket, never a subset: skills reference sibling skills by relative script paths (for example `enqueue` invokes `queue-status`'s script), so a partial copy breaks at runtime.
- Overwrite idempotently; the repo state wins over any drifted deployed copy.
- Do not write outside the resolved target.
- Do not edit the `skills-user/` sources.

## After

Newly deployed skills appear in `$`/`/` autocomplete only in sessions started after deployment; suggest a session restart/reload if discovery matters now. Report the list of deployed skill names and the target directory.
