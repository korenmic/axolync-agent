# 190 - P2 Agent Bootstrap Contract Repo Rename Fix

## Summary

Rename the deprecated repo-name string `axolync-plugins-contract` to the current name `axolync-contract` across the documentation of the core Axolync repos, so docs stop pointing at a repo name that no longer exists. This is a docs-only, exact-string search-and-replace; no code, packaging, or path behavior changes.

## Product Context

The contract authority repo was renamed to `axolync-contract` (its name on GitHub, in the local clone, and in its own README title "Axolync Contract"). The deprecated string `axolync-plugins-contract` still appears across the core repos. An audit of the exact string found:

- Total: 173 occurrences in 71 files across `axolync-agent`, `axolync-browser`, `axolync-contract`, `axolync-builder`.
- 164 (in 65 files) are in documentation (`.md`) and are plain references to the repo -> these are this seed's scope.
- 8 occurrences are in code and 1 in a `.json`; all 9 are intentional references to the deprecated name (stale-name detection constants, guard/refusal tests, an alias-rejection test, a migration description). Out of scope here; covered by a separate builder seed.
- Some `.md` lines are migration-describing (contain both the old and new name, e.g. "renamed from X to Y"). A blind replace would corrupt them, so they are left as historical references.

This is exactly the drift the bootstrap mirror-maintenance rule says the agent docs (and the wider docs) must not carry.

## Technical Constraints

- Docs-only: rename the exact string `axolync-plugins-contract` -> `axolync-contract` only in `.md` files. No code, `.json`, or fixture changes.
- Exclude the 9 code/`.json` occurrences entirely (intentional deprecated-name references; the separate builder seed handles any retirement).
- Exclude any `.md` line that also contains `axolync-contract` (migration-describing lines); leave them as historical, do not self-corrupt them into "from axolync-contract to axolync-contract".
- Keep the vocabulary entry's meaning accurate: the repo covers provider, addon-package, and repo-descriptor contracts, not only "plugin-facing" interfaces.
- No behavior change.

## Vocabulary Candidate Additions

- `Contract` (repo `axolync-contract`): the cross-repo contract/schema authority for provider, addon-package, and repo-descriptor interfaces. Replaces the stale `Plugins Contract` / `axolync-plugins-contract` naming.
- Retain `Plugins Contract` only as a single stale-historical-alias mention, so future agents recognize old references without treating it as a current name.

## Proposed Change

- Across the `.md` docs of `axolync-agent`, `axolync-browser`, `axolync-contract`, and `axolync-builder`: replace the exact string `axolync-plugins-contract` with `axolync-contract`, skipping migration-describing lines (those that also contain `axolync-contract`).
- In `axolync-agent` specifically this includes `bootstrap/axolync.vocabulary.md` (heading `Plugins Contract` -> `Contract`; broaden the meaning line; add one `Aliases / older wording: Plugins Contract` stale line), `bootstrap/repo-summaries.md`, and `bootstrap/axolync-builder.bootstrap-prompt.md`.

## Open Questions

- None. The alias-retention decision (drop `Plugins Contract` as a primary name; keep exactly one stale-historical-alias mention) is captured in the Vocabulary Candidate Additions and Proposed Change sections above.
