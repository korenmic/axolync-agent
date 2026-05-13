---
name: masterify-all
description: Move all Axolync repos known to the current workspace builder registry to master and update them. Use when the user asks to masterify all repos, return all repos to master, checkout master everywhere, or normalize the workspace after PR/build branches.
---

# Masterify All

Use the shared script:

```powershell
python axolync-agent/scripts/workspace_repo_ops.py status --workspace-root .
python axolync-agent/scripts/workspace_repo_ops.py masterify --workspace-root .
```

## Rules

- Run only in the current workspace root or pass `--workspace-root` explicitly.
- Operate only on `axolync-builder/config/repos.json` consumed repos plus `axolync-builder` itself.
- Do not touch arbitrary sibling folders or other agents' workspaces.
- Start with `status`. Dirty repos are blockers.
- Before masterifying a dirty repo, intentionally handle the dirty state:
- Commit track-worthy source changes.
- Remove or ignore generated build artifacts.
- Stop and ask/report when the dirty state is ambiguous.
- `masterify` fetches origin, checks out `master`, then rebases/pulls from `origin/master`.
- Local non-master branches are not deleted. The operation only switches the checkout after the repo is clean.

## Useful Commands

```powershell
python axolync-agent/scripts/workspace_repo_ops.py status --workspace-root . --json
python axolync-agent/scripts/workspace_repo_ops.py masterify --workspace-root . --dry-run
python axolync-agent/scripts/workspace_repo_ops.py masterify --workspace-root . --continue-on-error
```
