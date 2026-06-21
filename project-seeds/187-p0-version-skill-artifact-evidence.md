# 187 - P0 Version Skill Artifact Evidence

## Summary

Teach agent version skills to inventory and verify generated artifact version evidence in addition to primary repo version files, so future version bumps preserve the new authority standard.

## Product Context

The existing version skills operate on `versionFile` and tags. They do not detect stale addon ZIP manifests or browser preinstalled consumer metadata after a version bump.

## Technical Constraints

- Agent should continue using builder-declared repos only.
- Version authority remains the configured `versionFile`.
- Generated artifact evidence must be reported and verified, not treated as independent authority.
- Skill docs must tell future agents to regenerate/check package and browser metadata after bumps.

## Open Questions

None. User approved updating agent skills when version authority behavior changes.
