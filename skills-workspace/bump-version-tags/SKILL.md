---
name: bump-version-tags
description: Plan and apply controlled minor version/tag bumps for selected or all Axolync repos known to the current builder registry. Use when the user asks to bump repo versions/tags, release-bump selected repos, or push coordinated version tags.
---

# Bump Version Tags

Use the shared workspace script. Always plan first unless the user explicitly asked to apply immediately.

```powershell
python axolync-agent/scripts/workspace_version_ops.py plan-bump --workspace-root .
python axolync-agent/scripts/workspace_version_ops.py apply-bump --workspace-root . --yes --push
python axolync-agent/scripts/workspace_version_ops.py verify --workspace-root .
```

## Rules

- Run only in the current Axolync workspace root or pass `--workspace-root`.
- Operate only on `axolync-builder/config/repos.json` consumed repos plus `axolync-builder` itself.
- Do not scan arbitrary sibling folders.
- Default bump is one minor version, with prerelease suffix dropped, for example `2.0.0-beta.1 -> 2.1.0`.
- Repos with no tracked version file are tag-only only when the plan says so explicitly.
- Dirty repos, non-master repos, missing semver sources, and tag collisions are blockers by default.
- `apply-bump` requires `--yes`.
- Pushes require `--push`. When the user directly asks to push, push both commits and annotated tags.
- Do not force-push.
- After applying, run `verify` and provide the before/after table.
- Generated addon package ZIP manifests and browser preinstalled consumer metadata are evidence, not authority. A complete bump must regenerate/check that evidence so it matches the configured repo `versionFile`.
- If `verify` reports `blocked-artifact-evidence-drift`, regenerate the affected addon package ZIPs and browser preinstalled metadata before pushing a version bump as complete.

## Useful Commands

```powershell
python axolync-agent/scripts/workspace_version_ops.py plan-bump --workspace-root . --repo axolync-builder --repo axolync-browser
python axolync-agent/scripts/workspace_version_ops.py apply-bump --workspace-root . --repo-file ci-group-repos.txt --yes --push
python axolync-agent/scripts/workspace_version_ops.py verify --workspace-root . --repo-file ci-group-repos.txt
```
