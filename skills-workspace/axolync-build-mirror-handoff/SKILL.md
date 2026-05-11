---
name: axolync-build-mirror-handoff
description: Build Axolync APK/desktop artifacts and mirror reports for PR branches requested by another Sinq/Codex agent. Use when a dispatch asks Sinq1 to build, rebuild, run report, run no-ci/partial-ci/full-ci/nightly-safe CI, produce APK/EXE/Tauri/Electron artifacts, or mirror outputs to E:. Enforces Sinq1-only build execution and read-only treatment of other agents' workspaces.
---

# Axolync Build Mirror Handoff

## Purpose

Use this skill when another Sinq agent asks Sinq1 to build reviewed Axolync PR branches and mirror artifacts.

Sinq1 is the single build authority. Other workspaces may contain useful branch context, but they are not build locations.

## Authority Gate

Before performing any checkout, dependency install, test, build, report, or mirror action, run:

```text
py C:\Users\koren\src\Sinq\axolync-agent\scripts\resolve_dispatch_authority.py --workspace <current_workspace> --identity <local_identity_if_known>
```

If the helper returns `mode: "pass-through"` or anything other than `mode: "route"`, stop. Do not execute build/mirror work from this skill. Report that build authority is disabled for this workspace and that Sinq1 must perform the handoff.

## Hard Workspace Boundary

Build only under:

- `C:\Users\koren\src\Sinq`

Allowed in another agent workspace:
- Read branch names, task files, logs, evidence, and PR context.
- Write a root-level result file only when explicitly requested.

Forbidden in another agent workspace:
- Do not checkout, fetch, or pull.
- Do not clone repos.
- Do not install dependencies or toolchains.
- Do not run tests, builds, reports, or mirror commands.
- Do not create `.builder-links`, `.tools`, `output`, `artifacts`, generated files, or symlinks.
- Do not edit source files.

Before any build/report command, verify:
- current directory is under `C:\Users\koren\src\Sinq`
- all repo paths are under `C:\Users\koren\src\Sinq`
- builder path is `C:\Users\koren\src\Sinq\axolync-builder`
- toolchain path, if used, is under `C:\Users\koren\src\Sinq\axolync-builder\.tools`
- mirror destination is `E:\artifacts\axolync` or another explicitly requested non-workspace path
- no path resolves under `C:\Users\koren\src\Sinq2`, `Sinq3`, `Sinq4`, or any other agent workspace

If any check fails, stop and report the blocker.

## Branch Handling

When a dispatch references branches checked out in another workspace:

1. Treat those branches as remote branch names only.
2. Fetch the relevant remotes in Sinq1-local repos.
3. Check out or use builder repo-ref overrides in Sinq1-local repos only.
4. Record exact resolved commits used in the final summary.

## CI Modes

Use the requested mode:

- `no-ci`: artifact build/report only, usually `npm run build:all -- --skip-tests` plus `npm run report:noci -- --mirror-destination E:\artifacts\axolync\`.
- `partial-ci`: run only requested or latest-added focused tests, then build/report.
- `full-ci`: run the standard testful builder flow.
- `nightly-safe`: use the `nightly-ci-safe` skill from this workspace skill set and obey its rerun limits.

If no mode is specified, ask only if ambiguity affects runtime or cost materially. Otherwise prefer the normal artifact/report flow requested by the dispatch.

## Desktop Artifact Rule

Do not silently substitute Electron for Tauri.

If Tauri is expected and fails:
- report the Tauri blocker exactly
- only produce Electron as an explicitly labeled fallback if the request permits fallback artifacts

## Mirror Rule

Do not invent mirror paths.

Use builder/report mirror flow and the configured/requested root:

- `E:\artifacts\axolync\`

After mirroring, report exact paths for:
- HTML report
- JSON report
- repo-ref snapshot when present
- APK artifacts
- desktop portable/workspace artifacts
- blockers or fallbacks

## Notifications

If the request asks to notify:
- notify on start
- notify on meaningful progress
- notify on completion or blocker

Use concise notifications. Do not include long logs.
