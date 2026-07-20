# Requirements - Contract Repo Rename (Docs)

Derived from `project-seeds/190-p2-agent-bootstrap-contract-repo-rename-fix.md`.

## R1. Correct the deprecated repo name in agent bootstrap docs

- In `axolync-agent`, the three bootstrap docs that reference the contract repo must use the current name `axolync-contract`, not the deprecated `axolync-plugins-contract`:
  - `bootstrap/axolync.vocabulary.md`
  - `bootstrap/repo-summaries.md`
  - `bootstrap/axolync-builder.bootstrap-prompt.md`

## R2. Exact-string, docs-only

- Replace only the exact string `axolync-plugins-contract` with `axolync-contract`.
- Do not change code, JSON, or fixtures.
- Do not alter migration-describing lines that contain both the old and new name (none expected in these three files, but the rule holds).

## R3. Vocabulary entry accuracy

- In `axolync.vocabulary.md`, the vocabulary entry heading `Plugins Contract` becomes `Contract`; the meaning line is broadened to "provider, addon-package, and repo-descriptor interfaces"; and a single `Aliases / older wording: Plugins Contract` stale line is added so old references remain recognizable.

## R4. No behavior change

- Docs-only. A new bootstrapping agent resolves the contract repo to a name that exists on GitHub and locally.

## Note on wider scope

- Seed 190 also documents the same exact-string rename across `.md` docs in browser, contract, and builder (~153 more occurrences). Those are delivered as separate per-repo PRs; this spec/PR covers the agent bootstrap docs (the seed's home and the bootstrap-correctness core).
