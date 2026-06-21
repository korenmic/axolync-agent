---
name: version-tags-table
description: Regenerate a read-only Axolync workspace version/tag table for repos known to the current builder registry. Use when the user asks to list, view, regenerate, save, or inspect all repo tags/versions.
---

# Version Tags Table

Use the shared workspace script:

```powershell
python axolync-agent/scripts/workspace_version_ops.py inventory --workspace-root .
```

## Rules

- Run only in the current Axolync workspace root or pass `--workspace-root`.
- Operate only on `axolync-builder/config/repos.json` consumed repos plus `axolync-builder` itself.
- Do not scan arbitrary sibling folders.
- This skill is read-only. Do not commit, tag, push, checkout, pull, or mutate repos.
- The default output is a CLI-shaped `.txt` file in the workspace root.
- Use `.md` only when explicitly useful for a handoff.
- `current` remains the authority version from the repo `versionFile` or latest semver tag.
- The artifact evidence column reports generated package/browser metadata alignment only; it is not an alternate version authority.

## Useful Commands

```powershell
python axolync-agent/scripts/workspace_version_ops.py inventory --workspace-root . --output -
python axolync-agent/scripts/workspace_version_ops.py inventory --workspace-root . --repo axolync-builder --repo axolync-browser
python axolync-agent/scripts/workspace_version_ops.py inventory --workspace-root . --format md
python axolync-agent/scripts/workspace_version_ops.py inventory --workspace-root . --json-output VERSION_TAGS_latest.json
```
