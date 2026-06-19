# Requirements

## Summary

Align agent-facing full-CI language with Builder's split between maximal `full-ci` validation and reduced `full-ci-core` validation.

## Acceptance Criteria

- `full-ci` is documented as maximal descriptor-aware validation.
- `full-ci-core` is documented as reduced/core-only validation.
- Merge-proof, nightly-safe, and maximal-validation guidance must not treat report-only, no-ci, dry-run, GitHub-only, or core-only runs as full-CI proof.
- Guidance for explicitly reduced/core validation must name `full-ci-core`.
- The wording preserves the existing rule that implementation agents should not dispatch to Sinq unless the user explicitly authorizes dispatch.
- Static tests cover the command naming contract without running Builder, dispatching Sinq, rebuilding artifacts, or regenerating reports.
