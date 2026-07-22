---
name: temp-headless-smoke
description: "Run temporary, untracked Playwright headless-browser smoke tests against a non-default local Axolync browser server, infer relevant checks from the current feature or bug context, clean up temporary servers/artifacts, and report tests performed. Use when invoked as $temp-headless-smoke or when Codex must visually confirm a browser DOM flow such as SongSearch result rendering and click-through."
---

# Temporary Headless Smoke

Use this workspace skill when the user authorizes temporary headless browser smoke testing for an Axolync feature, bug fix, or PR branch.

This skill is a workspace-only testing workflow. Do not install or copy it into `~/.codex/skills`.

## Shortcut

Use `$temp-headless-smoke` as the canonical shortcut.

## Test Design Responsibility

Infer and design the relevant temporary headless checks yourself from:

- the current task
- the latest agreed design
- the suspected risk areas
- the visible UI or runtime behavior being validated

Do not require the user to provide exact scripts, click paths, or assertions unless the behavior is genuinely ambiguous. Choose the page flows, clicks, waits, assertions, and diagnostics that best prove or disprove the current design.

Keep temporary smoke coverage scoped to the current proof target. Do not expand into broad exploratory testing unless the user explicitly asks.

## Temporary Server And File Hygiene

When a browser app server is needed, start a temporary server on a non-default port. Do not take over the user's normal development port.

Track the temporary server process you start and terminate it before finishing the turn. If process cleanup fails, report the PID, port, and attempted cleanup command.

Keep throwaway screenshots, logs, and scratch data untracked. Remove them before finishing unless the user explicitly asks to keep a specific artifact.

When reporting results, include:

- the temporary port used
- each temporary headless test performed
- whether temporary scripts or logs were removed or intentionally kept
- whether the temporary server was killed

## Reusable Script

Use the bundled script for normal Axolync browser smoke flows:

```powershell
rtk node C:\Users\koren\src\Sinq2\.codex\skills\temp-headless-smoke\scripts\temp-headless-smoke.mjs --browser-root C:\Users\koren\src\Sinq2\axolync-browser
```

For SongSearch result-panel proof:

```powershell
rtk node C:\Users\koren\src\Sinq2\.codex\skills\temp-headless-smoke\scripts\temp-headless-smoke.mjs `
  --browser-root C:\Users\koren\src\Sinq2\axolync-browser `
  --query "Black Hole Sun" `
  --active-songsearch-addon axolync-addon-lrclib `
  --active-songsearch-adapter lrclib-songsearch `
  --expect-panel `
  --click-first `
  --click-candidate-index 1 `
  --screenshot C:\Users\koren\src\Sinq2\.codex\tmp\temp-headless-smoke-songsearch.png
```

Use `--click-candidate-index` with `--click-first` when the intended proof target is not the first visible result, for example when Manual fallback renders before provider-backed SongSearch results.

If addon manifests/packages changed, run browser `predev` first so preinstalled ZIPs are current, then restore accidental generated manifest/version drift before reporting.

## Scoped Fix And Retest Rule

If a temporary headless test proves a bug in the latest agreed design, you may fix that bug in scope and rerun the relevant temporary test immediately.

Only fix the proven issue. Do not use this skill as permission for unrelated cleanup, broad refactors, behavior expansion, or permanent test infrastructure unless the user separately approves that work.

Temporary smoke tests are evidence, not a replacement for committed unit tests, CI, artifact rebuilds, or manual merge gates. If a feature still needs those checks, say so explicitly.

Report:

- the bug the temporary test proved
- the scoped fix applied, if any
- the temporary test rerun after the fix
- any remaining validation that still belongs outside this temporary smoke pass
