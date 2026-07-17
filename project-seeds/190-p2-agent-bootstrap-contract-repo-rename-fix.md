# 190 - P2 Agent Bootstrap Contract Repo Rename Fix

## Summary

Correct the stale repo name `axolync-plugins-contract` to the real repo name `axolync-contract` across the `axolync-agent` bootstrap surface, so a new bootstrapping agent resolves the contract authority repo to a name that actually exists on GitHub and in the local clone set.

## Product Context

The contract authority repo is named `axolync-contract` on GitHub, in the local clone, and in its own README title ("Axolync Contract"). Three mirrored bootstrap docs in `axolync-agent` still use the stale name `axolync-plugins-contract`:

- `bootstrap/axolync.vocabulary.md` -- the `Plugins Contract` heading and its `Repo:` line
- `bootstrap/repo-summaries.md` -- the `## axolync-plugins-contract` section heading
- `bootstrap/axolync-builder.bootstrap-prompt.md` -- the sibling-repo clone list

A new agent following the bootstrap prompt would try to bootstrap a nonexistent `axolync-plugins-contract` sibling and would resolve contract authority to the wrong name. This is a bootstrap-correctness defect in exactly the mirror-maintenance surface `axolync-agent` is responsible for keeping current.

## Technical Constraints

- Rename references only; do not restructure the docs.
- Keep the vocabulary entry's meaning accurate: the repo covers provider, addon-package, and repo-descriptor contracts, not only "plugin-facing" interfaces.
- Docs-only change; no code or behavior change.
- This correction is precisely the kind of drift the bootstrap mirror-maintenance rule says the agent bootstrap docs must not carry.

## Vocabulary Candidate Additions

- `Contract` (repo `axolync-contract`): the cross-repo contract/schema authority for provider, addon-package, and repo-descriptor interfaces. Replaces the stale `Plugins Contract` / `axolync-plugins-contract` naming.

## Proposed Change (pre-drafted, approved in principle)

- `axolync.vocabulary.md`: heading `Plugins Contract` -> `Contract`; meaning line broadened to "provider, addon-package, and repo-descriptor interfaces"; `Repo:` `axolync-plugins-contract` -> `axolync-contract`.
- `repo-summaries.md`: `## axolync-plugins-contract` -> `## axolync-contract`.
- `axolync-builder.bootstrap-prompt.md`: clone-list `axolync-plugins-contract` -> `axolync-contract`.

## Open Questions

- Keep `Plugins Contract` as an explicit alias line under the renamed `Contract` vocabulary entry, or drop it entirely? (Seed author leans drop, since the repo never actually carried that name.)
