# Android Wrapper Reference Inventory Triage

## Summary

Inventory every remaining `axolync-android-wrapper`, `android-wrapper`, and old Android-wrapper-shaped reference across Axolync repos, then produce a decision ledger that splits cleanup into small reviewable micro-scopes. This seed is parent/inventory-only: it should not remove or rename runtime code by itself.

## Product Context

The old Android wrapper repo identity has been retired in favor of platform-wrapper ownership. The cleanup is risky because some references may be pure repo-name debt while others may be runtime concepts, bridge names, legacy compatibility labels, docs, tests, or historical migration notes.

The user specifically wants to avoid approving too many case-by-case changes at once. This seed exists to prevent broad over-approval by forcing a compact ledger and micro-seed split before implementation.

## Technical Constraints

- This seed is P2 and inventory-only.
- Do not mutate product code as part of this seed.
- Scan all Axolync repos known to the builder registry plus the agent repo.
- Classify each reference by repo, file, symbol/string, and risk level.
- Do not treat every occurrence as a simple rename.
- Do not resurrect old `*-wrapper` repo paths or remotes.
- Output a decision ledger and proposed micro-seeds.
- Cap each future Browser/runtime micro-seed to a small number of cases.

## Proposed Scope

1. Build the reference inventory.
   - Search for `axolync-android-wrapper`, `android-wrapper`, `android wrapper`, and close casing variants.
   - Include docs/tests/scripts/config/runtime code.
   - Record whether the reference is repo identity, runtime mode, bridge label, command path, documentation, test fixture, or historical note.

2. Classify references.
   - `mechanical`: repo name/path/docs/config with no runtime behavior.
   - `browser-runtime-sensitive`: Browser code that may affect runtime behavior or compatibility.
   - `platform-token-sensitive`: platform-wrapper tokens/enums/bridges that may be legitimate Android runtime naming.
   - `docs-only`: historical or explanatory docs.
   - `do-not-touch`: references that are intentional historical audit evidence.

3. Produce a ledger.
   - Include exact file paths and concise rationale.
   - Recommend the destination micro-seed per reference.
   - Mark unreviewed sensitive references as blocked until separately approved.

4. Produce or update micro-seeds.
   - Builder/agent mechanical cleanup.
   - Browser runtime sensitive audit.
   - Platform-wrapper token parity audit.
   - Addon/docs cleanup.

## Resolved Decisions

- This parent seed should birth or update micro-seeds but should not execute their cleanup.
- Sensitive Browser/runtime cases must not be bundled into one large approval.
- Mechanical cleanup can be grouped separately only if the ledger proves no runtime behavior is involved.

## Open Questions

- Which discovered references, if any, should be marked `do-not-touch` as historical audit evidence? Answer after the inventory ledger exists.
