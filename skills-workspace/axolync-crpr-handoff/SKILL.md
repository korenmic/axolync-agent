---
name: axolync-crpr-handoff
description: Review Axolync PRs for another Sinq/Codex agent and produce the CRPR.md ping-pong handoff. Use when a dispatch asks for CR PR MD, CRPR.md, PR review, re-review after fixes, or no-action-items confirmation for branches checked out in another workspace. Enforces read-only access to other agents' workspaces except writing the requested CRPR.md file at that workspace root.
---

# Axolync CRPR Handoff

## Purpose

Use this skill when another Sinq agent asks Sinq1 to review Axolync PRs and write a `CRPR.md` handoff.

This skill is for review only. Do not implement fixes unless the user explicitly changes the task.

## Authority Gate

Before performing CRPR handoff work, run:

```text
py .\axolync-agent\scripts\resolve_dispatch_authority.py --workspace <workspace-root> --identity <local_identity_if_known>
```

If the helper returns `mode: "pass-through"` or anything other than `mode: "route"`, stop. Do not write `CRPR.md` from this skill. Report that CRPR authority is disabled for this workspace and that Sinq1 must perform the handoff.

## Workspace Boundary

Sinq1 is the CR authority, but other Sinq workspaces are not build/edit workspaces.

Allowed in another agent workspace:
- Read files to understand the checked-out branches, diffs, task files, or local evidence.
- Write exactly the requested root-level `CRPR.md` handoff file.

Forbidden in another agent workspace:
- Do not checkout branches.
- Do not fetch or pull.
- Do not install dependencies.
- Do not run tests/builds/reports.
- Do not edit source files.
- Do not create links, generated artifacts, cloned repos, or toolchains.

If source checkout is needed for deeper review, fetch and checkout the PR branches under Sinq1's workspace:

- `<workspace-root>`

## Review Workflow

1. Identify the PRs, repos, branches, latest commits, and stated review scope from the dispatch.
2. Derive a stable `group-key` from the requested PR URLs and branch names.
3. Before local checkout work, run:

```text
py .\axolync-agent\scripts\dispatch_checkout_state.py restore-stale --workspace-root <workspace-root> --group-key <group-key>
```

4. Before changing each local repo away from its current branch, record its previous checkout:

```text
py .\axolync-agent\scripts\dispatch_checkout_state.py record --workspace-root <workspace-root> --dispatch-id <dispatch-id> --group-key <group-key> --repo-id <repo-id> --repo-path <repo-path>
```

5. Prefer local repos under `<workspace-root>` for diff inspection. Use another workspace only as read-only evidence.
6. Do not restore at CRPR completion; same-PR ping-pong follow-ups may still need those branches. The next unrelated dispatch restores stale state.
7. Review with a code-review mindset:
   - correctness bugs
   - behavioral regressions
   - missing or weak tests
   - build/report integration risks
   - cross-repo contract mismatches
8. For ping-pong rounds, focus on newly pushed fixes and whether prior action items are resolved.
9. Write `CRPR.md` only if requested.

## CRPR.md Format

Use concise Markdown.

If findings remain:

```markdown
# CRPR Review

## <repo / PR>

- [severity] <actionable finding with file/line if possible>. Impact: <why it matters>. Required fix: <what Sinq should change>.
```

If clean:

```markdown
# CRPR Review

No action items remain.
```

## Final Response

State whether `CRPR.md` is complete and whether action items remain. Keep the response short.
