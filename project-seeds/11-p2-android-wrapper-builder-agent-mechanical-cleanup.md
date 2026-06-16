# Android Wrapper Builder And Agent Mechanical Cleanup

## Summary

Clean up low-risk `android-wrapper` repo-identity references in builder and agent sources after the parent inventory proves they are mechanical. This seed should not touch Browser runtime behavior or platform-wrapper runtime token semantics.

## Product Context

Builder and agent code should no longer instruct agents, reports, registry commands, or bootstrap flows to use the retired Android wrapper repo identity. Mechanical references should point to `axolync-platform-wrapper` or be removed when obsolete.

## Technical Constraints

- This seed is P2.
- Scope is builder and agent repos only unless the parent inventory explicitly identifies another low-risk tooling-only repo.
- Do not touch Browser runtime source.
- Do not touch platform-wrapper runtime enums/bridge tokens.
- Do not change historical docs unless the parent inventory classifies them as active guidance rather than history.
- Add regression tests or static guards for active bootstrap/registry output when practical.

## Proposed Scope

1. Use the parent inventory ledger as input.
2. Rename active tooling references from Android wrapper repo identity to platform-wrapper.
3. Remove obsolete compatibility aliases only where no current command or registry needs them.
4. Add/update tests that prove active generated guidance no longer emits the old repo name.
5. Leave sensitive or ambiguous references for their own micro-seeds.

## Resolved Decisions

- This is the only micro-seed allowed to perform broad mechanical replacements.
- Mechanical means "active guidance/config points to a retired repo name" and must be proven before editing.

## Open Questions

- None until the parent inventory identifies exact mechanical references.
