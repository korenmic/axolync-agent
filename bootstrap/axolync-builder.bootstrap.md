# Axolync Agent Bootstrap

This is the single entry file for bootstrapping a new AI coding agent into Axolync.
If you need a ready-to-paste orientation prompt for a fresh AI instance, see [bootstrap-prompt.md](bootstrap-prompt.md).

Do not start by reading the entire repo tree.
Start here, follow the order below, then narrow to the active task.

## Goal

Bring a new agent to a useful working level quickly by:
- reading the highest-value authority docs first
- learning the critical product model early
- bootstrapping the workspace in the fastest safe way
- avoiding broad unfocused reading

## Bootstrap Mirror Maintenance Rule

The docs mirrored into `axolync-agent/bootstrap/` are not archival copies.
They are part of the current Axolync agent bootstrap surface and must stay in sync with the repos they summarize.

If any repo-defining core thing changes, update the relevant `axolync-agent` bootstrap docs in the same change or immediately adjacent follow-up:

- repo role or ownership boundaries
- workspace/bootstrap workflow
- seed/spec/task execution norms
- queue/task-id conventions
- vocabulary that new agents need in order to interpret the repos correctly
- critical authority reading order

TACTIC clarification:

- queue and TACTIC execution metadata belong under the top-level workspace `.codex/` tree
- they do not belong under any individual repo root
- if an agent is editing `C:\Users\koren\src\Sinq\axolync-browser`, the session state still belongs at `C:\Users\koren\src\Sinq\.codex\tactic\session.json`

Do not let `axolync-agent` drift into stale orientation material.
If the source repo meaning changes, the mirrored bootstrap explanation here must change with it.

## Authority Order

When docs disagree, prefer this order unless the active task explicitly says otherwise:
- current browser runtime authority docs for product behavior
- current contracts docs for provider/query compatibility authority
- builder docs for bootstrap/workflow/reporting authority
- android-wrapper docs for host-shell packaging/runtime-host concerns only
- legacy handoff or archived docs as background only, not as primary authority

## Read Order

### 1. Builder operating surface

Read these first:
- [README.md](README.md)
- [config/build-presets/README.md](config/build-presets/README.md)
- [vocabulary.md](vocabulary.md)
- [chat.md](chat.md)
- [docs/seed-execution-guide.md](docs/seed-execution-guide.md)

These establish:
- repo topology
- preset/build TOML language and CLI behavior
- project-specific terms
- long-chat hygiene
- seed/spec/task execution workflow

### 2. Critical product authority

Read this next, early:
- [../axolync-browser/docs/state-machine-interaction-matrix.md](../axolync-browser/docs/state-machine-interaction-matrix.md)

This is one of the most important early product authority docs because it defines:
- states
- state-machine events
- official query inventory
- state-to-query authority
- query-to-event reference

If the task touches addons, adapters, query dispatch, arbitration, live playback flow, or controller behavior, this file is mandatory early reading.

### 3. Current addon/runtime authority

If the task touches the new addon host shape, also read:
- [.codex/specs/migration-08-app-side-addon-host-prep-and-contract-hardening/requirements.md](.codex/specs/migration-08-app-side-addon-host-prep-and-contract-hardening/requirements.md)
- [.codex/specs/migration-08-app-side-addon-host-prep-and-contract-hardening/design.md](.codex/specs/migration-08-app-side-addon-host-prep-and-contract-hardening/design.md)
- [.codex/specs/migration-08-app-side-addon-host-prep-and-contract-hardening/tasks.md](.codex/specs/migration-08-app-side-addon-host-prep-and-contract-hardening/tasks.md)
- [../axolync-browser/docs/legacy-demo-retirement-inventory.md](../axolync-browser/docs/legacy-demo-retirement-inventory.md)

These are the current authority docs for:
- addon ZIP shape
- manifest/admission/registry behavior
- state-query binding
- Stage 1 demo proof
- legacy demo retirement gate

### 4. Task-local repo context

Only after the above:
- read the target repo README/workflow if it exists
- inspect the exact code seams relevant to the assigned task
- avoid broad repo-wide reading unless the task truly requires it

## Fast Workspace Bootstrap

## Git Editor Rule

Before any Git command that might invoke an editor, set a noninteractive `GIT_EDITOR` in the same shell.

Required PowerShell form:

```powershell
$env:GIT_EDITOR='true'
```

Required bash/sh form:

```bash
export GIT_EDITOR=true
```

This is a hard rule, not a preference.
Do not rely on the machine-default Git editor, because it may open a manual editor such as Notepad++ and block autonomous progress.
Apply this before commands such as:

- `git rebase`
- `git pull --rebase`
- `git commit` when Git may open an editor
- `git merge` when Git may open an editor
- any other Git flow that could fall back to editor-driven message entry or conflict handling

### Builder-only shallow clone

If the goal is fast deployment/bootstrap rather than deep history analysis:

```bash
gh repo clone korenmic/axolync-builder -- --depth=1 --single-branch --branch master
```

```powershell
gh repo clone korenmic/axolync-builder -- --depth=1 --single-branch --branch master
```

### Bootstrap sibling repos

From the builder root:

```bash
./scripts/bootstrap-axolync-repos.sh --shallow
```

```powershell
.\scripts\bootstrap-axolync-repos.ps1 -Shallow
```

This gives a fast latest-commit sibling workspace without cloning full history first.
The managed sibling set now also includes:

- `axolync-addon-demo-stage1` as the extracted Stage 1 demo-addon source repo
- `axolync-songmetadata-plugin` as the SongMetadata atlas/report adapter-inventory source

If full history is needed later for one repo:

```bash
git -C /path/to/repo fetch --unshallow --tags origin
```

```powershell
git -C C:\path\to\repo fetch --unshallow --tags origin
```

### Recommended first commands

From the builder root after bootstrap:

```bash
npm run versions:sync
node scripts/generate-platform-report.mjs --dry-run
```

Those give:
- a truthful repo snapshot
- a quick report surface without waiting for full CI/build execution

## Parallel Agent Rules

For multiple agents working at once:
- prefer one separate workspace per writing agent
- split ownership by repo or by non-overlapping file slices
- avoid multiple agents editing the same file family at the same time
- keep one agent as the integrator when work spans several repos

The safest default is:
- one top-level clone set per active coding agent

## Working Style

When starting a real implementation task:
1. identify the exact active seed/spec/task
2. read the authority docs above
3. inspect the concrete code seams
4. run the smallest meaningful verification first
5. keep changes scoped to the assigned task

Do not assume older legacy shapes are still the authority just because they exist in code.
Preserve current working behavior, but treat the settled spec and authority docs as the target model.
