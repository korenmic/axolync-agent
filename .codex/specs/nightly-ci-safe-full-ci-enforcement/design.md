# Design

## Overview

Update the `nightly-ci-safe` skill to call builder's canonical `full-ci` command and verify its proof metadata. The skill remains a cost-control wrapper: one full-CI inventory pass, then narrow reruns only for fix verification.

## Skill Behavior

The skill text should make these facts unambiguous:

- Full nightly validation starts with builder `full-ci`.
- `report:generate`, `report:noci`, `report:generate:dry`, sanity, smoke, GitHub-only metadata, and stale reused evidence are forbidden substitutions.
- Candidate-inventory proof is useful for implementation validation but is not executed full-nightly success.
- The skill must inspect proof metadata before declaring green.

## Checklist

The skill's final response checklist should include:

- command used
- run preset
- full-CI proof status
- executed test count
- not-run count
- browser full-CI status
- builder full-CI status
- artifact and mirror status if requested
- blockers/fix commits

## Verification

Add agent-side tests or static validation that read the skill file and assert required phrases/guards are present. This keeps the policy stable without needing to run full CI during implementation.
