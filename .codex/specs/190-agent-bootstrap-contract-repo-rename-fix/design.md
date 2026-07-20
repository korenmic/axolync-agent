# Design - Contract Repo Rename (Docs)

Derived from `requirements.md` in this spec folder.

## Files and exact edits

### `bootstrap/axolync.vocabulary.md`
- Heading `### Plugins Contract` -> `### Contract`.
- Meaning line -> "The cross-repo contract/schema authority for provider, addon-package, and repo-descriptor interfaces."
- `Repo:` `axolync-plugins-contract` -> `axolync-contract`.
- Add one line: `Aliases / older wording: Plugins Contract` (marked stale/historical).

### `bootstrap/repo-summaries.md`
- Section heading `## axolync-plugins-contract` -> `## axolync-contract`.

### `bootstrap/axolync-builder.bootstrap-prompt.md`
- Sibling-repo clone list entry `axolync-plugins-contract` -> `axolync-contract`.

## Method
- Targeted edits (exact string / heading), not a blind sed, so the vocabulary heading rename + alias line are applied precisely and no unrelated `Plugins`/`Contract` text is touched.
- Verify after: `git grep -l axolync-plugins-contract -- bootstrap/*.md` returns nothing.

## Out of scope
- Code/JSON occurrences (builder seed 195), and the browser/contract/builder docs (separate per-repo PRs).
