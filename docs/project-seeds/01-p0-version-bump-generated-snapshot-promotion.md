# P0 Generated Artifact Authority Hygiene: Version-Bump Snapshot Promotion

## Summary

Update Axolync agent version-bump infrastructure so release/version bump runs regenerate volatile generated truth first, then promote that truth into tracked release snapshot files before committing and tagging.

## Related Seed Group

- Browser seed 213 owns volatile generated outputs and Browser runtime/build consumers.
- Builder seed 191 owns release/artifact evidence validation for tracked snapshots.
- Agent seed 01 owns version-bump skill behavior that promotes regenerated volatile truth into tracked release snapshots.

## Product Context

Generated Browser files are useful release evidence, but they should not be dirtied by ordinary dev runs. The release/tag flow is the correct time to refresh tracked generated snapshots because that is when a stable source snapshot is intentionally being published.

## Technical Constraints

- Never assume an existing generated file is fresh.
- Version-bump flow must regenerate volatile generated truth before copying/promoting tracked snapshots.
- Promotion must be explicit and visible in the resulting release/version-bump commit.
- The skill should not silently stage unrelated generated dirt.
- This seed may require coordination with Browser seed 213's volatile output paths and Builder seed 191's validation command.

## Proposed Design

1. Teach the version-bump skill/infrastructure which repos expose generated artifact snapshot promotion hooks.
2. For Browser, run the generation funnel that produces volatile generated truth before version bump commit creation.
3. Copy approved volatile generated outputs into tracked release snapshot paths.
4. Run Builder release snapshot validation before final commit/tag.
5. Report promoted snapshot files in the version-bump summary.

## Acceptance Criteria

- Patch/minor version-bump flow refreshes tracked generated release snapshots intentionally.
- The flow does not rely on stale pre-existing generated files.
- The final version-bump report lists generated snapshots that were promoted.
- Builder release snapshot validation passes after promotion.
