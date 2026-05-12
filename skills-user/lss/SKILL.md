---
name: lss
description: List currently available Codex skills from user and workspace skill roots. Use when invoked as $lss, ls-skills, or when the user asks to list loaded/available skills.
---

# List Skills

Use this skill to produce a concise inventory of currently available Codex skills.

## Scope

List skills from the active agent environment, not from memory alone.

Check these roots when they exist:

- User-global skills: `~/.codex/skills`
- Workspace skills: `<current workspace>/.codex/skills`

If a workspace skill root is a junction or symlink, report the resolved target when it is easy to determine.

## Output

Return a simple grouped list:

- user skills
- workspace skills
- system/plugin skills if they are visible in the session skill list but not found under the two filesystem roots

For each skill, include:

- skill name
- short description when available from `SKILL.md`
- path

If a root is missing or unreadable, say that explicitly and continue with the other roots.

## Guardrails

- Do not edit skills while listing them.
- Do not install missing skills.
- Do not scan full repositories recursively; only inspect direct child skill folders and their `SKILL.md`.
