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
py .\axolync-agent\scripts\resolve_dispatch_authority.py --workspace <workspace-root> --identity <local_identity_if_known>
```

If the helper returns `mode: "pass-through"` or anything other than `mode: "route"`, stop. Do not execute build/mirror work from this skill. Report that build authority is disabled for this workspace and that Sinq1 must perform the handoff.

## Hard Workspace Boundary

Build only under the current primary workspace root:

- `<workspace-root>`

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
- current directory is under `<workspace-root>`
- all repo paths are under `<workspace-root>`
- builder path is `<workspace-root>\axolync-builder`
- toolchain path, if used, is under `<workspace-root>\axolync-builder\.tools`
- mirror destination is `E:\artifacts\axolync` or another explicitly requested non-workspace path
- no path resolves under another agent workspace

If any check fails, stop and report the blocker.

## Branch Handling

When a dispatch references branches checked out in another workspace:

1. Treat those branches as remote branch names only.
2. Fetch the relevant remotes in local repos under `<workspace-root>`.
3. Derive a stable `group-key` from the requested PR URLs and branch names.
4. Before local checkout work, run:

```text
py .\axolync-agent\scripts\dispatch_checkout_state.py restore-stale --workspace-root <workspace-root> --group-key <group-key>
```

5. Before changing each local repo away from its current branch, record its previous checkout:

```text
py .\axolync-agent\scripts\dispatch_checkout_state.py record --workspace-root <workspace-root> --dispatch-id <dispatch-id> --group-key <group-key> --repo-id <repo-id> --repo-path <repo-path>
```

6. Check out or use builder repo-ref overrides in local repos under `<workspace-root>` only.
7. Do not restore at dispatch completion; same-PR follow-up dispatches may still need those branches. The next unrelated dispatch restores stale state.
8. Record exact resolved commits used in the final summary.

## CI Modes

Use the requested mode:

- `no-ci`: artifact build/report only, usually `npm run build:all -- --skip-tests` plus `npm run report:noci -- --mirror-destination E:\artifacts\axolync\`.
- `partial-ci`: run only requested or latest-added focused tests, then build/report.
- `full-ci`: run Builder's maximal descriptor-aware validation flow. This is the only full-CI merge-proof mode; do not satisfy it with report-only, no-ci, dry-run, sanity, GitHub metadata, inventory-only evidence, or `full-ci-core`.
- `full-ci-core`: run Builder's reduced/core-only validation flow. Use this only when the dispatch explicitly asks for reduced/core validation, and label the result as reduced rather than full merge proof.
- `nightly-safe`: use the `nightly-ci-safe` skill from this workspace skill set and obey its rerun limits.

If no mode is specified, ask only if ambiguity affects runtime or cost materially. Otherwise prefer the normal artifact/report flow requested by the dispatch.

## Long Command Execution

For dispatched build, report, mirror, and CI commands, use the boring direct command path.

Required:
- Run long builder commands directly through RTK, for example `rtk npm run build:all -- --skip-tests`.
- Prefer builder-native logs and generated output files for diagnosis.
- If a direct command exits with unclear output, inspect existing builder output/log files after the command exits.
- If extra logging is unavoidable, use a bounded helper that exits with the child process and has been proven not to hold the dispatch open.

Forbidden for long dispatched commands:
- Do not pipe build/report/CI commands through `Tee-Object`, `tee`, transcript wrappers, or equivalent live logging pipelines.
- Do not make an outer logging wrapper the condition for dispatch completion.
- Do not leave stale wrapper processes alive after the underlying builder command exits.

Reason: dispatch waits for the receiving Codex turn to finish. A wrapper pipeline can remain alive after the real builder process exits, causing a false dispatch hang even when artifacts were already built.

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
