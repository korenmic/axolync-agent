# Axolync Agent

Axolync Agent is the shared coordination surface for bootstrapping Axolync coding agents, preserving repo/workspace rules, and publishing workspace-scoped Codex skills.

## Skill Buckets

The repo deliberately separates skills by installation scope.

- `skills-workspace/`: skills safe to expose to a single Axolync workspace through a workspace-local `.codex/skills` junction.
- `skills-user/`: reusable user-level skills that may duplicate `C:\Users\koren\.codex\skills`; bootstrap agents must not install or link these into the user Codex directory unless the user explicitly asks for a specific skill.

Do not junction or copy the entire historical `skills/` folder. Use only `skills-workspace/` for workspace discovery.

## Workspace Skills Junction

A bootstrap agent is allowed to create a workspace-local junction from the workspace root `.codex\skills` directory to this repo's `skills-workspace` directory, as long as both paths remain inside the same workspace.

For the Sinq1 workspace, run from an elevated or normal `cmd` session:

```cmd
mklink /J "C:\Users\koren\src\Sinq\.codex\skills" "C:\Users\koren\src\Sinq\axolync-agent\skills-workspace"
```

Before creating the junction:

- Confirm `C:\Users\koren\src\Sinq\.codex\skills` does not already exist.
- If it exists, inspect it and ask before replacing anything.
- Confirm the target is `C:\Users\koren\src\Sinq\axolync-agent\skills-workspace`.

After creating the junction, restart or reload the Codex session if `$` skill autocomplete does not refresh immediately.

## User Skill Installation Policy

Bootstrap agents must not install `skills-user/` into `C:\Users\koren\.codex\skills` automatically.

User-level installation is allowed only when the user explicitly requests it for a named skill. This avoids duplicating or shadowing skills that are already installed globally.

## Workspace Boundary Reminder

Sinq1 is the Axolync CR and build authority. Build/report/mirror work must run in `C:\Users\koren\src\Sinq` using Sinq1-local repo checkouts and builder tooling.

Other Sinq workspaces are read-only evidence sources unless a dispatch explicitly requests a root-level handoff file such as `CRPR.md`.

The primary dispatch, CRPR, and build/mirror skills are guarded by `scripts/resolve_dispatch_authority.py`. In workspaces whose identity is not `Sinq` or `Sinq1`, those skills must fail closed instead of routing into primary-authority workflows.
