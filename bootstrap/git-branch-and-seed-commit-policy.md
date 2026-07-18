# Git Branch & Seed-Commit Policy

This is a hard workflow rule for Axolync agents. It defines the single case where a
commit may land directly on `master`, and requires everything else to go through a
branch and a reviewed pull request.

## The One Direct-To-Master Exception

Creating a brand-new feature seed file is the only thing an agent may commit directly
to `master`, and only as a single new file under a repo's seed directory
(for example `axolync-agent/project-seeds/` or `axolync-builder/docs/project-seeds/`).

Rules for the exception:

- It applies to creating a NEW seed file only.
- One new seed file per direct-to-master commit.
- Editing an existing seed, or changing any other file in the same commit, does not qualify.
- Seed commits are "launch and forget": the seed is a proposal for later review, not implemented work.

## Everything Else Goes Through a Branch and PR

All other changes must be made on a branch and merged through a pull request:

- spec trios (`requirements.md`, `design.md`, `tasks.md`)
- implementations of a seed's tasks
- edits to an existing seed
- documentation, README, and bootstrap-doc changes
- skill additions or edits
- fixes of any kind

The implementation of a seed always lives on its own branch, never on `master`.

## Merge Is Human-Only

An agent never merges a pull request. Merging is a human action, gated by the project's
merge-readiness review: automated CI plus any manual, human-run tests the agent asks the
human to perform. See the check-merge-ready workflow for the readiness criteria.

## Why This Policy Exists

- Keeps `master` history clean: proposals (seeds) are cheap to add, but real work is always reviewable before it lands.
- Prevents an agent from silently changing shipped behavior without a review gate.
- Makes seeds a low-friction idea inbox while keeping implementation disciplined.
