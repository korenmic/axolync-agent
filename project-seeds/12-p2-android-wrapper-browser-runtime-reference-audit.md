# Android Wrapper Browser Runtime Reference Audit

## Summary

Review Browser-side `android-wrapper` references case by case and decide whether each is obsolete repo-identity debt, legitimate Android runtime/platform behavior, or historical compatibility evidence. This seed should be split further if more than a few runtime-sensitive cases are found.

## Product Context

Browser should not know about retired wrapper repos as runtime dependencies. However, Browser may legitimately know about Android/Capacitor runtime capabilities such as microphone override, native host routing, or platform-specific runtime modes. Those cases must not be renamed blindly.

## Technical Constraints

- This seed is P2 and review-heavy.
- Do not perform broad search/replace.
- Cap each implementation pass to a small number of Browser cases.
- For each case, document why it exists and what flow uses it.
- Keep Android/Capacitor runtime behavior intact.
- If a reference is only a repo name/path, prefer platform-wrapper or removal.
- If a reference is a runtime mode/token, prove whether changing it is safe before editing.
- Add focused tests for any runtime behavior changed.

## Proposed Scope

1. Read the parent inventory Browser references.
2. For each Browser case, classify:
   - retired repo dependency
   - active Android runtime concept
   - native bridge/host routing concept
   - historical test/doc fixture
3. Propose the minimal action per case:
   - remove
   - rename to platform-wrapper
   - keep as Android runtime naming
   - move to historical docs
4. Implement only explicitly approved cases.
5. Add focused guards so old repo dependencies do not return.

## Resolved Decisions

- Browser runtime references are not safe for one-shot cleanup.
- `androidbridge`-style names may be legitimate runtime flow names and need proof before rename.
- Repo identity debt and runtime platform vocabulary must be separated.

## Open Questions

- Which Browser references are active runtime platform concepts rather than retired repo-identity debt? Answer from code evidence during this seed.
