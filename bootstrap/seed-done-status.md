# Seed Done-Status Management

How to record that an Axolync seed is completed, so reports and dashboards stop showing finished work as remaining. Read this before marking any seed done.

## Where done-status lives

- **Builder** (`axolync-builder`): the authority is `config/seed-metadata.json` — an `entries` map keyed by repo-relative seed path. `config/seed-priority.json` is priority-only, NOT done-state. A test, `tests/seed-metadata-consistency.test.mjs`, enforces that every builder seed file has a metadata entry.
- **Other repos** (browser, contract, whisper, ...): most do NOT have a `config/seed-metadata.json`. Their status is tracked (if at all) by an in-file `Status:` line in the seed markdown, and/or inferred by the builder report from merged PRs / spec folders. Treat this as weaker than the builder mechanism.

## To mark a BUILDER seed done

1. Update (or add) its entry in `config/seed-metadata.json`, keyed by the repo-relative seed path (e.g. `axolync-builder/docs/project-seeds/NNN-...md`).
2. Set:
   - `status: "completed"`
   - `merged: true`
   - `completedCommit: <merge/impl commit sha>`
   - `completedAt: <ISO timestamp>` when known
3. Keep the seed/spec `tasks.md` checkboxes aligned (all `[x]` when done).
4. Run/expect `tests/seed-metadata-consistency.test.mjs` (it enforces registration + shape).

New (not-yet-done) builder seeds must still be registered, typically as `status: "draft"`, `merged: false`, with `addedCommit` (or the placeholder `pending-local`), `addedAt`, `summary`, and `affectedRepos`.

## To mark a NON-builder seed done

- Update the seed markdown's `Status:` line to reflect the merged implementation, e.g. `Status: Implemented (PR #NNN, merged <date>)`.
- There is no per-repo `seed-metadata.json` to update in most repos; if a browser/other-repo status authority is added later, prefer it over the `Status:` line.
- Proof of "done" is a merged PR whose title/branch names the seed index. Verify that before flipping status.

## Why this matters

A merged seed that still shows `Status: Seed` (or is unregistered in builder metadata) makes completed work look remaining. Both browser `216` (DSR retirement, merged as PR #169) and browser `202` (safe playbar widget render host, merged as PR #159) were merged yet still showed stale `Status: Seed`. Always confirm via the merged PR and update the correct authority for that repo.
