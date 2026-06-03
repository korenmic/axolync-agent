# Tasks

## 1. Refresh nightly-safe command vocabulary

- [x] 1.1 Replace `full-ci:inventory` references with `full-ci -- --dry-run`.
- [x] 1.2 Clarify that dry-run output is candidate listing only, not executed proof.
- [x] 1.3 Keep `npm run full-ci` as the one broad validation command.

## 2. Update strict continuation guidance

- [x] 2.1 Update post-fix continuation wording to use `full-ci:remaining`.
- [x] 2.2 Make strict remaining evidence distinct from candidate dry-run listing.
- [x] 2.3 Preserve the at-most-one broad full-CI run rule.

## 3. Harden invalid-proof reporting

- [x] 3.1 Require `FULL CI PROOF NOT VALID` for unreconciled candidate/executed counts.
- [x] 3.2 Require invalid-proof reporting for report-only/no-ci/sanity/dry-run/GitHub-only substitutions.
- [x] 3.3 Require invalid-proof reporting for collapsed Browser rows or mostly `not_run` reports.

## 4. Verify skill text

- [x] 4.1 Add or update static tests for the skill vocabulary.
- [x] 4.2 Run focused agent tests for nightly-safe skill text.
