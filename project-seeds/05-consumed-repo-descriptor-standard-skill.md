# Consumed Repo Descriptor Standard Skill

## Summary

Upgrade the `axolync-add-consumed-repo` workspace skill so future Axolync repos are created and registered using the new descriptor-owned standard required by the CI-group builder modernization.

The skill must no longer guide agents toward legacy `config/repos.json` command/package/inventory fallback metadata for new repos. It should require repo-owned `axolync.repo.toml` exports for tests, packaging, generated outputs, inventories, docs, and repo consumption whenever those surfaces apply.

## Priority

- `P0`

## Product Context

The CI-group builder branch treats legacy `config/repos.json` fallback usage as red descriptor migration debt. A recently created OffGrid repo exposed the risk: if agents keep using the old onboarding style, new repos can immediately create red warnings in modern builder reports.

This seed updates the agent-side source of future behavior. It is not backwards compatibility work. It is future-proofing: new repos should be created in the modern descriptor-owned format by default.

## Technical Constraints

- Repository: `axolync-agent`.
- Branch: new CI-group branch `seed-005-consumed-repo-descriptor-standard`.
- Do not edit user-global `~/.codex` skills.
- Update the repo-tracked/workspace skill source only.
- No backwards-compatible alternate old-school path.
- No instruction should tell future agents to add new repo-owned command/package/inventory authority to builder `config/repos.json`.
- Builder-owned fields can still exist in builder configuration only for builder-owned concerns:
  - repo id
  - local path
  - submodule path
  - submodule URL
  - version authority
  - cleaning/bootstrap hints when genuinely builder-owned
- Repo-owned descriptor exports must cover applicable:
  - tests
  - packaging commands and outputs
  - generated outputs
  - adapter/catalog inventories
  - docs and project seeds
  - consumed repo dependencies
  - addon-pack member declarations
  - native companion metadata when applicable

## Required Outcomes

1. The `axolync-add-consumed-repo` skill must state that new repos use descriptor-owned exports as the only accepted authority for repo-owned surfaces.
2. The skill must explicitly reject adding legacy `config/repos.json` fallback fields for new repos:
   - `buildCommands`
   - `sanityCommands`
   - `testCommands`
   - `addonPackage`
   - `adapterCatalogManifestPath`
   - `adapterCatalogManifestProfileId`
3. The skill must tell agents to add builder-side tests that prove no descriptor fallback warnings are emitted for the new repo when its descriptor is available.
4. The skill must include an onboarding checklist that verifies `axolync.repo.toml` exports before builder/report wiring is considered complete.
5. The skill must preserve the workspace boundary rule: never use another agent workspace for repo creation, checkout, build, or mutation.
6. The skill must still allow builder-owned consumed-repo discovery data where necessary, but must name it as builder-owned and separate from repo-owned exports.

## Open Questions

Resolved for spec-making:

1. This is a strict upgrade to the new format, not a dual-mode/backwards-compatible skill.
2. The target is future repo creation/onboarding behavior, not retroactive repair of every existing repo.
3. This belongs to the CI-group PR set because the CI-group report standard is what exposes these warnings as merge blockers.

## Completion Criteria

1. The skill source is updated in `axolync-agent`.
2. The old-school fallback guidance is removed or replaced with descriptor-owned guidance.
3. New repo onboarding instructions require descriptor-owned exports for repo-owned surfaces.
4. The final skill text is explicit enough that future OffGrid-like repos do not recreate descriptor fallback warnings.

