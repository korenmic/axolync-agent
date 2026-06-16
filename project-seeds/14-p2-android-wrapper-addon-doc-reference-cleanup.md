# Android Wrapper Addon And Docs Reference Cleanup

## Summary

Clean up low-risk addon, pack, theme, and documentation references to the retired Android wrapper repo identity after the parent inventory identifies them as docs-only or active guidance. This seed excludes Browser runtime and platform-wrapper token changes.

## Product Context

Addon and docs repos may still mention old wrapper names in README snippets, setup instructions, historical notes, or tests. Active guidance should use platform-wrapper. Historical references can remain only when clearly marked as historical and not current setup guidance.

## Technical Constraints

- This seed is P2.
- Scope is addon/pack/theme/docs references classified by the parent inventory.
- Do not edit runtime code outside documentation/test fixtures unless explicitly approved.
- Do not change Browser runtime behavior.
- Do not change platform-wrapper public tokens.
- Prefer precise edits over broad replacement.

## Proposed Scope

1. Use the parent inventory addon/docs references as input.
2. Update active setup/build guidance to `axolync-platform-wrapper`.
3. Remove obsolete references that imply the retired repo still exists.
4. Preserve historical references only when explicitly labeled historical.
5. Add a simple static docs guard if repeated drift is likely.

## Resolved Decisions

- Active docs should not tell agents or users to use `axolync-android-wrapper`.
- Historical mentions can remain only when they cannot be confused with current instructions.

## Open Questions

- None until the parent inventory identifies exact docs/addon references.
