# Tasks

- [x] 1. Audit agent-facing full-CI wording in relevant skills and tests.
- [x] 2. Update `$nightly-ci-safe` guidance so `full-ci` means maximal descriptor-aware proof and `full-ci-core` means reduced/core-only validation.
- [x] 3. Update build/mirror handoff wording so Sinq1 dispatches interpret `full-ci` as maximal proof and use `full-ci-core` only for explicitly reduced validation.
- [x] 4. Add or update static tests that guard the command vocabulary and invalid-proof exclusions.
- [x] 5. Validate locally with focused agent tests only; do not dispatch Sinq, rebuild artifacts, or regenerate reports.
