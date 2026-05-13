---
name: pull-all-repos
description: Pull/update all Axolync repos known to the current workspace builder registry. Use when the user asks to pull all repos, fetch all repos, update all local Axolync repos, or keep current non-master branches while updating known consumed repos. Uses builder-declared consumed repos only and ignores ad hoc sibling clones.
---

# Pull All Repos

Use the shared script:

```powershell
python axolync-agent/scripts/workspace_repo_ops.py status --workspace-root .
python axolync-agent/scripts/workspace_repo_ops.py pull --workspace-root .
```

## Rules

- Run only in the current workspace root or pass `--workspace-root` explicitly.
- Operate only on `axolync-builder/config/repos.json` consumed repos plus `axolync-builder` itself.
- Do not scan arbitrary sibling folders. Temporary CR/session clones are ignored unless builder declares them as consumed repos and their folder basename matches the repo id.
- Start with `status`. If any repo is dirty, inspect and resolve it before pulling.
- Commit only intentional, track-worthy source changes. Do not commit generated artifacts or build outputs.
- If dirty state is ambiguous, stop and report the blocker instead of auto-stashing or auto-committing.
- `pull` preserves the current branch. On master it rebases from origin/master; on non-master branches it rebases from the branch upstream when one exists and otherwise fetches only.
- Use `masterify-all` when the user wants all known repos moved to master.

## Useful Commands

```powershell
python axolync-agent/scripts/workspace_repo_ops.py status --workspace-root . --json
python axolync-agent/scripts/workspace_repo_ops.py pull --workspace-root . --dry-run
python axolync-agent/scripts/workspace_repo_ops.py pull --workspace-root . --continue-on-error
```
