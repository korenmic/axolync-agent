# Axolync Bootstrap Prompt

This file is a copy-paste bootstrap prompt for a fresh AI instance that needs fast, safe Axolync orientation.

Use this together with [bootstrap.md](bootstrap.md), which remains the authority doc.
If later work should be staged or batch-executed through a local queue, also use [queue-guidance.md](queue-guidance.md).

```text
Bootstrap Axolync orientation in the current workspace only.
This turn is orientation only, not implementation or execution proof.

Hard rules:
- Write only inside the current workspace.
- Do not touch sibling repos or parent folders outside the current workspace root.
- Before any Git command that might invoke an editor, set a noninteractive `GIT_EDITOR` in the same shell. PowerShell: `$env:GIT_EDITOR='true'`. Bash/sh: `export GIT_EDITOR=true`.
- This is mandatory. Do not rely on the machine-default Git editor, because it may open a manual editor such as Notepad++ and block autonomous progress.
- Clone `korenmic/axolync-builder` into the current workspace with `gh`, shallow.
- Then bootstrap these sibling repos as shallow siblings under that same workspace only:
  - `axolync-browser`
  - `axolync-android-wrapper`
  - `axolync-plugins-contract`
  - `axolync-addon-whisper`
  - `axolync-addon-vibra`
  - `axolync-addon-lrclib`
  - `axolync-addon-demo-stage1`
  - `axolync-addon-itunes`
  - `axolync-addon-spotify`
  - `axolync-addon-musicbrainz`
  - `axolync-songmetadata-plugin`
  - `axolync-lyricflow-plugin`
  - `axolync-songsense-plugin`
  - `axolync-syncengine-plugin`
- If `axolync-builder/scripts/bootstrap-axolync-repos.ps1` or `axolync-builder/scripts/bootstrap-axolync-repos.sh` can do that while staying entirely inside the current workspace, prefer it with a workspace-local base dir plus shallow mode.
- Do not run builds, tests, CI, reports, packaging, APK generation, `versions:sync`, or long verification flows.
- Read only the docs listed below. For long docs, skim examples, install steps, and CI snippets unless they change authority, workflow, topology, runtime model, or compatibility rules.
- Treat docs with `/home/deck/...` or other machine-specific paths as potentially stale unless confirmed by newer root docs.
- Deprioritize `docs/notes/`, `docs/presentations/`, `*.html`, old handoffs, `PLAN*`, `FUTURE_PLANS.md`, `ai-local-system.md`, and deprecated docs unless directly referenced by the required docs.
- Ignore archived material by default:
  - any path under an `archived/` subtree, or under a directory containing `.axolync-archive-policy.json`, is out of normal orientation scope
  - do not surface `cancelled`, `suspended`, or `superseded` seeds/specs in routine summaries unless the user explicitly asks for archived or stale history
- If persistent tracked workspace state suddenly disappears, downgrades unexpectedly, or looks corrupted, stop immediately. Do not delete, reclone, restore, bootstrap, or “heal” anything autonomously. Report the anomaly and wait for explicit user direction.
- Notify rule: if local notify config exists, send the final ready notification with the repo notify script; otherwise report that notify is blocked by missing config and do not invent config.
- If a workspace-local execution queue already exists under the workspace root `.codex/`, treat it as durable local coordination state rather than keeping the queue only in memory.
- Do not create repo-local `TACTIC` metadata such as `<repoRoot>/.codex/tactic/`; session state belongs only at `<workspaceRoot>/.codex/tactic/`.

Read in this exact order:
1. builder: `README.md`, `bootstrap.md`, `ai.md`, `config/build-presets/README.md`, `vocabulary.md`, `docs/seed-execution-guide.md`
2. browser: `README.md`, `docs/state-machine-interaction-matrix.md`, `docs/client-server-policy.md`, `docs/runtime-boundary-review-checklist.md`, `docs/ai-global.md`
3. contracts: `README.md`, `tools/README.md`, `VERSIONING.md`, `COMPATIBILITY.md`
4. builder seeds: `docs/project-seeds/20-single-clone-builder-bootstrap-and-redeployment.md`, `31-environment-specific-path-and-host-assumption-audit.md`, `33-builder-build-presets-toml-and-env-demotion.md`, `docs/project-seeds/migration/08-contracts-logical-vs-transport-hardening.md`, `32-migration-08-readiness-hardening-meta-seed.md`
5. then repo orientation only: android-wrapper `README.md`, whisper `README.md`, lyricflow `README.md`, songsense `README.md`, syncengine `README.md`, songmetadata `README.md`

Final output:
- repo topology
- authority map
- most important things to know next
- stale-doc / portability cautions
- what you intentionally skipped or deprioritized
- elapsed time
- final ready notification result
```
