---
name: axolync-crpr-handoff
description: Review Axolync PRs for another Sinq/Codex agent and produce the CRPR.md ping-pong handoff. Use when a dispatch asks for CR PR MD, CRPR.md, PR review, re-review after fixes, or no-action-items confirmation for branches checked out in another workspace. Enforces read-only access to other agents' workspaces except writing the requested CRPR.md file at that workspace root.
---

# Axolync CRPR Handoff

## Purpose

Use this skill when another Sinq agent asks Sinq1 to review Axolync PRs and write a `CRPR.md` handoff.

This skill is for review only. Do not implement fixes unless the user explicitly changes the task.

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

- `C:\Users\koren\src\Sinq`

## Review Workflow

1. Identify the PRs, repos, branches, latest commits, and stated review scope from the dispatch.
2. Prefer Sinq1-local repos for diff inspection. Use another workspace only as read-only evidence.
3. Review with a code-review mindset:
   - correctness bugs
   - behavioral regressions
   - missing or weak tests
   - build/report integration risks
   - cross-repo contract mismatches
4. For ping-pong rounds, focus on newly pushed fixes and whether prior action items are resolved.
5. Write `CRPR.md` only if requested.

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
