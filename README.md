# Axolync Agent

New agent? Start with the reading order: [bootstrap/recommended-reading.md](bootstrap/recommended-reading.md).

## Deploying Skills

Three deployment skills install this repo's skills. They are readable procedures — a cold agent can execute them straight from these files BEFORE any skill is installed, and gets the same result as running the installed skill:

- [`skills-user/deploy-userspace-skills/SKILL.md`](skills-user/deploy-userspace-skills/SKILL.md) — deploy the whole `skills-user/` bucket into the running agent's userspace (Codex or Claude, auto-detected).
- [`skills-user/deploy-workspace-skills/SKILL.md`](skills-user/deploy-workspace-skills/SKILL.md) — expose `skills-workspace/` to the current workspace (Codex junction / Claude claudify output).
- [`skills-user/deploy-skills/SKILL.md`](skills-user/deploy-skills/SKILL.md) — umbrella: both of the above, always both scopes.

Invoked as `$deploy-skills` / `$deploy-userspace-skills` / `$deploy-workspace-skills` (Codex) or the `/name` forms (Claude) once installed.

Axolync Agent is the shared coordination surface for bootstrapping Axolync coding agents, preserving repo/workspace rules, and publishing workspace-scoped Codex skills.

## Git Workflow Policy

Read before committing: [bootstrap/git-branch-and-seed-commit-policy.md](bootstrap/git-branch-and-seed-commit-policy.md). It also defines **per-task implementation discipline**: implementing a task ticks its `tasks.md` checkbox in the same commit (one task, one commit) — the TACTIC rule.

## Seed Done-Status

How to mark a seed completed (builder `config/seed-metadata.json` vs the `Status:` line in other repos): [bootstrap/seed-done-status.md](bootstrap/seed-done-status.md).

## Skill Buckets

The repo deliberately separates skills by installation scope.

- `skills-workspace/`: skills safe to expose to a single Axolync workspace through a workspace-local `.codex/skills` junction.
- `skills-user/`: reusable user-level skills that may duplicate the user-level Codex skills directory; bootstrap agents must not install or link these into the user Codex directory unless the user explicitly asks for a specific skill.

Do not junction or copy the entire historical `skills/` folder. Use only `skills-workspace/` for workspace discovery.

## Cross-Agent Skill Exposure (Codex vs Claude)

Skill sources are authored once in the Codex shape (the `$name` invocation prefix) and exposed differently depending on which agent is bootstrapping:

- Codex: junction `<workspace>\.codex\skills` to `skills-workspace` (see below); skills are invoked as `$name`.
- Claude: run `scripts/claudify.py` (the `$claudify` workspace skill) to generate Claude-form copies under the gitignored `.claudify-out/`, auto-install the workspace copies into `<workspace>\.claude\skills`, and invoke skills as `/name`. User skills are generated too but are installed globally only by hand.

The Codex `$name` sources stay the single source of truth; claudify produces the Claude copies on demand and never edits the sources.

## Workspace Skills Junction

A bootstrap agent is allowed to create a workspace-local junction from the workspace root `.codex\skills` directory to this repo's `skills-workspace` directory, as long as both paths remain inside the same workspace.

From a workspace root, run from an elevated or normal `cmd` session:

```cmd
mklink /J ".codex\skills" "axolync-agent\skills-workspace"
```

Before creating the junction:

- Confirm `<workspace-root>\.codex\skills` does not already exist.
- If it exists, inspect it and ask before replacing anything.
- Confirm the target is `<workspace-root>\axolync-agent\skills-workspace`.

After creating the junction, restart or reload the Codex session if `$` skill autocomplete does not refresh immediately.

## User Skill Installation Policy

Bootstrap agents must not install `skills-user/` into the user-level Codex skills directory automatically.

User-level installation is allowed only when the user explicitly requests it for a named skill. This avoids duplicating or shadowing skills that are already installed globally.

## Workspace Boundary Reminder

Sinq1 is the Axolync CR and build authority. Build/report/mirror work must run from the current primary workspace root using that workspace's local repo checkouts and builder tooling.

Other Sinq workspaces are read-only evidence sources unless a dispatch explicitly requests a root-level handoff file such as `CRPR.md`.

The primary dispatch, CRPR, and build/mirror skills are guarded by `scripts/resolve_dispatch_authority.py`. In workspaces whose identity is not `Sinq` or `Sinq1`, those skills must fail closed instead of routing into primary-authority workflows.
