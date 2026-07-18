# 192 - P2 Seed Execution Guide Ownership Migration

## Summary

Migrate the AI-directed policy portions of `axolync-builder/docs/seed-execution-guide.md` into `axolync-agent`, leave the builder-machinery portions in builder (reframed as builder report/artifact mechanics rather than "seed execution policy"), drop the redundant portions, and fix the file's stale machine-specific paths as a byproduct. The principle: AI-directed policy should live only in the agent repo; builder should not own AI workflow policy.

## Product Context

`axolync-builder/docs/seed-execution-guide.md` is currently pointed to from the agent bootstrap reading order as the operator handoff for turning a seed into working code. Reviewing it shows it mixes three different kinds of content under one "policy" framing:

1. AI-directed workflow policy (belongs in agent).
2. Builder report/artifact machinery (legitimately builder-owned implementation truth).
3. Redundant material already covered elsewhere.

It also contains stale absolute paths copied from one contributor's Linux machine (for example `/home/deck/src/axolync-builder/ai.md`), which are dead links on any other machine, including this Windows workspace.

## Content Breakdown And Ownership Decision

### Migrate into agent (AI-directed policy)

- Seed-to-spec self-review workflow (create `requirements.md`, self-review, then `design.md`, self-review, then `tasks.md`).
- The "every new seed needs a Vocabulary Candidate Additions section" rule.
- Commit-message format rules (commit title = task number + task title; commit body = the completed task text; no unrelated work mixed into a task commit).
- Task-execution ordering (the TACTIC-style order: update task, implement scoped change, add tests, run smallest verification, check the task box, commit code + tests + task state together, notify, final closeout task).
- The final "do not drift from the seed's intended ownership boundaries" rule.

Dedupe rule during migration: much of this is already partly covered by existing agent skills (spec-maker, s2s, enqueue, implement, tactic, notify). Migrate only the genuinely unique statements and reference the existing skills for the rest, instead of re-duplicating skill bodies into a doc.

### Keep in builder (report/artifact machinery, not policy)

- The adapter-seed rule: `*.fit.json` sidecar as structured authority, candidate class, upstream snapshot, method-fit matrix, and the licensing-evidence requirement.
- The seed-registration recipe: `config/seed-metadata.json` entry, presentation files, and post-report verification against `artifacts/output/latest/knowledge/feature-seeds/`.

These describe how builder's report/atlas system works. They are builder implementation truth, not AI workflow policy, so they should stay in builder. Reframe the surrounding language so the builder file reads as "builder report/seed mechanics," not "the seed execution policy."

### Drop as redundant

- The "Meaning Of A Repo" section duplicates `axolync-agent/bootstrap/repo-summaries.md`.

## Proposed Implementation

1. Choose the agent destination for the migrated policy (new agent-owned policy doc vs folding into existing bootstrap docs/skills).
2. Move the AI-directed policy statements there, deduped against existing skills.
3. Trim the builder file to the builder-machinery sections only, reframed as mechanics; drop the redundant section.
4. Rewrite any surviving links in the builder file as relative paths, eliminating the stale `/home/deck/...` absolute paths.
5. Update the agent bootstrap reading order so it points at the new agent-owned policy for workflow rules, and at the trimmed builder file only for builder report/seed mechanics.

## Open Questions

- Exact agent destination: a single new agent-owned workflow-policy doc, or distribute the statements into the existing bootstrap docs and the relevant skills?
- Should the trimmed builder file keep a thin pointer back to the agent-owned policy, or carry no policy reference at all?
- Is any of the "keep in builder" machinery itself already stale and better dropped than preserved?
