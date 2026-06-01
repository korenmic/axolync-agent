# Tasks

- [x] 1. Update nightly-ci-safe skill to require builder `full-ci`
  - Replace ambiguous full-local/full-CI wording with canonical builder `full-ci`.
  - State that the first full inventory pass must call `full-ci`.
  - Preserve the one-full-CI-run limit.

- [x] 2. Add forbidden substitution guard language
  - Forbid `report:generate`, `report:noci`, `report:generate:dry`, `sanity`, smoke, GitHub-only metadata, stale reused evidence, and mostly `not_run` rows as full-nightly substitutes.
  - Require `full nightly not completed` wording when full-ci is blocked.

- [x] 3. Add proof-gate verification instructions
  - Require inspection of builder full-CI proof metadata before declaring success.
  - Distinguish executed full-CI success from candidate-inventory proof.
  - Require blocker reporting when the proof gate fails.

- [x] 4. Add final checklist requirements
  - Include command used, run preset, proof status, executed count, not-run count, browser status, builder status, artifact/mirror status, blockers, and fix commits.

- [x] 5. Add dispatch guard wording
  - Ensure incoming `$nightly-ci-safe` or full-nightly dispatches preserve the full-CI requirement under time pressure.
  - Clarify that short validation requests should use sanity, not nightly-safe.

- [x] 6. Add static tests or validation for the skill guard
  - Verify the skill references builder `full-ci`.
  - Verify forbidden substitutions are listed.
  - Verify proof-gate verification is required.
  - Verify candidate-inventory proof cannot be summarized as executed full nightly success.
