# Git Branch & Seed-Commit Policy

This is a hard workflow rule for Axolync agents. It defines the single case where a
commit may land directly on `master`, and requires everything else to go through a
branch and a reviewed pull request.

## The Direct-To-Master Exception: Seed Creation And Seed Hardening

Seed work — creating a new seed file, or hardening/editing an existing seed file — is
committed directly to `master`, always under a repo's seed directory
(for example `axolync-agent/project-seeds/` or `axolync-builder/docs/project-seeds/`).
Only seed IMPLEMENTATION goes through a branch and PR.

Rules for the exception:

- It applies to seed files only: creating a new seed, or hardening/editing an existing one.
- One seed file per direct-to-master commit; no non-seed files in the same commit.
- Seed commits are "launch and forget": the seed is a proposal for later review, not implemented work.
- Implementing a seed's tasks never qualifies — implementation always lives on its own branch and PR.

## Catalog Cut-And-Paste Exception (Seeds Graduating From A Catalog)

Catalog repos (for example `axolync-songsearch-adapters`) hold candidate entries that
graduate into real seeds in their destined repos. Graduating a candidate does NOT use
the direct-to-master seed exception. It is a two-PR cut-and-paste flow:

1. A PR in the catalog repo removing the candidate entry (the "cut").
2. A PR in the destination repo adding the seed file (the "paste"), opened as a PR,
   not committed to master.

Both PRs go through normal review/merge. The rest of the lifecycle (s2s, enqueue,
implement) proceeds from the destination repo only after its paste PR is merged.
Rationale: graduation changes two repos at once and retires catalog truth, so both
sides deserve a review gate even though the payload is a seed.

## Everything Else Goes Through a Branch and PR

All other changes must be made on a branch and merged through a pull request:

- spec trios (`requirements.md`, `design.md`, `tasks.md`)
- implementations of a seed's tasks
- documentation, README, and bootstrap-doc changes
- skill additions or edits
- fixes of any kind

The implementation of a seed always lives on its own branch, never on `master`.

## Per-Task Implementation Discipline

When implementing a task from a spec `tasks.md` or a backlog list, the commit that
implements the task MUST also tick that task's checkbox (`- [ ]` -> `- [x]`) in the
same `tasks.md`, staged in the same commit. A task is not "done" until its checkbox is
flipped in the same proof commit.

- One task, one commit: do not batch multiple tasks into a single commit.
- The checkbox flip is part of the proof, not a later cleanup pass.
- This is the TACTIC discipline (`skills-user/tactic/SKILL.md`, the
  `T = Tick the completed checkbox in the same proof commit` step). Running TACTIC's
  per-task loop enforces it automatically; implementing a task outside that loop is
  exactly where the checkbox flip gets skipped.

## Merge Is Human-Only

An agent never merges a pull request. Merging is a human action, gated by the project's
merge-readiness review: automated CI plus any manual, human-run tests the agent asks the
human to perform. See the check-merge-ready workflow for the readiness criteria.

## Why This Policy Exists

- Keeps `master` history clean: proposals (seeds) are cheap to add, but real work is always reviewable before it lands.
- Prevents an agent from silently changing shipped behavior without a review gate.
- Makes seeds a low-friction idea inbox while keeping implementation disciplined.
