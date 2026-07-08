# Design

## Overview

`refresh-workspace-skills` is a workspace maintenance skill. It updates the tracked source of workspace skills in `axolync-agent`, repairs or verifies the current workspace skill exposure, and reports whether the current Codex thread can use the updated skill list.

## Skill Location

Create:

```text
skills-workspace/refresh-workspace-skills/SKILL.md
```

No helper script is required for v1. The skill should describe the safe workflow and required checks. A later version may add a dry-run/repair script if the workflow becomes repetitive.

## Triggering

Frontmatter:

```yaml
name: refresh-workspace-skills
description: Pull latest axolync-agent master and apply or verify workspace skill exposure for the current workspace without installing skills into the user Codex homedir. Use when invoked as $refresh-workspace-skills or when workspace skills/autocomplete/runtime availability appear stale.
```

## Workflow

The skill directs agents to:

1. find `axolync-agent`
2. check dirty state
3. pull `origin/master` with fast-forward-only behavior
4. inspect current workspace `.codex/skills`
5. repair safe stale/missing exposure using existing bootstrap convention
6. verify visible workspace skill list against `axolync-agent/skills-workspace`
7. state whether active-session reload is possible or a new Codex session is needed

## Safety Boundaries

- Do not install workspace skills into `~/.codex/skills`.
- Do not mutate user-profile skills.
- Do not overwrite dirty workspace skill files.
- Do not claim dynamic reload if only disk state changed.
- Respect RTK/AGENTS command rules whenever active.

## Validation

The implementation is docs/skill validation. `$lssa` must list the new workspace skill. A lightweight content test can assert the key guardrails are present.

