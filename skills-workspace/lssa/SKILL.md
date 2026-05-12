---
name: lssa
description: List skills tracked inside the axolync-agent repository. Use when invoked as $lssa, ls-skills-axolync, or when the user asks for the tracked agents repo skill inventory.
---

# List Axolync Agent Skills

Use this skill to list the skill definitions tracked by the `axolync-agent` repository.

## Scope

Inspect only the current workspace's `axolync-agent` repository.

Skill roots to list:

- `skills-user`
- `skills-workspace`
- legacy `skills` if present

## Output

Return a grouped list by root.

For each skill, include:

- skill name from frontmatter
- folder name if different
- short description from frontmatter
- path

Also mention:

- folders missing `SKILL.md`
- invalid or unreadable `SKILL.md` files

## Guardrails

- Do not edit skills while listing them.
- Do not install tracked skills into `~/.codex/skills`.
- Do not include generated caches such as `__pycache__`.
