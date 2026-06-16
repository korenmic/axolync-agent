# Android Wrapper Platform Wrapper Token Audit

## Summary

Audit platform-wrapper references that still use Android-wrapper-shaped tokens, aliases, or names. Decide whether each token is a legitimate Android platform/runtime name or stale compatibility with the retired repo identity.

## Product Context

Platform-wrapper is the current repo and authority. It may still contain values such as Android bridge, Android runtime, or legacy aliases. Some may be valid because the platform is Android; others may be stale repo-rename compatibility.

## Technical Constraints

- This seed is P2.
- Do not remove aliases unless code evidence proves they are stale.
- Do not rename public/runtime contract values without compatibility review.
- Distinguish "Android as platform" from "android-wrapper as retired repo".
- Add tests for any enum/token/contract changes.
- Coordinate with Browser if Browser consumes any changed token.

## Proposed Scope

1. Use the parent inventory platform-wrapper references as input.
2. Classify each token as:
   - platform concept
   - repo identity debt
   - compatibility alias
   - public contract
3. Recommend keep/remove/rename per token.
4. Implement only low-risk or explicitly approved token changes.
5. Add compatibility tests for any changed public values.

## Resolved Decisions

- The repo name should be platform-wrapper.
- Android platform/runtime terms are not automatically wrong.
- Contract values require more care than docs/config strings.

## Open Questions

- Which aliases, if any, remain necessary for installed artifacts or older Browser versions? Answer from code and runtime contract references.
