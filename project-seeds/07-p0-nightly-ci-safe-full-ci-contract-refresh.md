# Nightly CI Safe Full-CI Contract Refresh

## Summary

Refresh the agent-owned `$nightly-ci-safe` skill so it uses Builder's corrected `full-ci` vocabulary and cannot depend on the removed `full-ci:inventory` concept.

## Priority

- `P0`

## Product Context

`$nightly-ci-safe` is the operator workflow that prevents repeated uncontrolled full-CI reruns. It must still demand real full-CI proof when the user or dispatch asks for nightly/full CI.

Builder's intended command model is now:

- `npm run full-ci` for the full proof workflow.
- `npm run full-ci -- --dry-run [--skip-list <file>]` for candidate listing only.
- `npm run full-ci:remaining [-- --ci-report <path>] [-- --skip-list <path>] [-- --dry-run]` for post-run remaining-test handling.

The agent skill must align with that model.

## Technical Constraints

- Repository: `axolync-agent`.
- Update the tracked workspace skill and any helper docs/tests it owns.
- Do not make the agent define its own full-CI semantics.
- Do not run the multi-hour full-CI suite as acceptance for this seed.
- Preserve the existing safety rule: one broad full-CI run at most per nightly-safe session.
- Post-fix continuation must use strict remaining-test evidence from Builder, not candidate inventory treated as pass proof.

## Required Behavior

1. Replace `full-ci:inventory` instructions with `full-ci -- --dry-run`.
2. Document that dry-run output is candidate listing only, never executed success.
3. Require `npm run full-ci` for the one allowed full-CI pass.
4. Require checking Builder's reconciliation/proof fields before declaring the run valid.
5. Use `full-ci:remaining` after fixes to identify remaining failed/unconfirmed tests.
6. Keep focused reruns constrained to the already-known failure batch.
7. Report `FULL CI PROOF NOT VALID` if candidate/executed counts are unreconciled, if Browser rows are collapsed, or if the run is substituted with report-only/no-ci/sanity/dry-run evidence.

## Definition Of Done

1. `$nightly-ci-safe` no longer references `full-ci:inventory`.
2. `$nightly-ci-safe` uses Builder `full-ci -- --dry-run` only as preflight candidate listing.
3. `$nightly-ci-safe` uses Builder `full-ci` as the mandatory full proof run for nightly/full-CI requests.
4. `$nightly-ci-safe` uses strict `full-ci:remaining` semantics for continuation.
5. Static validation or focused tests prove the skill text cannot regress to inventory-only proof wording.

## Open Questions

None. Use the resolved behavior in this seed.

