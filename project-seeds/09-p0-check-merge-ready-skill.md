# Check Merge Ready Skill

## Summary

Create a `$check-merge-ready` skill for Axolync PRs and PR groups. The skill should audit whether a PR or coordinated branch group is actually ready to merge by combining GitHub Actions status, local-only test coverage, CR approval evidence, warning/report quality, and explicit blocker reporting.

The skill is an audit/verdict workflow, not an implementation or merge workflow. It may wait for cloud checks to finish and may run approved local-only checks, but it must not merge PRs.

## Product Context

Axolync often uses multi-repo PR groups where merge readiness depends on more than one signal:

- GitHub Actions must be green for each PR where applicable.
- Local-only tests not covered by GitHub must be run or explicitly waived.
- CRPR review must be clean or have tracked unresolved findings.
- Builder/report artifacts must not hide red warnings when report or artifact proof is part of the merge criterion.
- Prior runs must not be mistaken for current branch-head evidence.

The purpose of `$check-merge-ready` is to produce a clear verdict that prevents over-trusting partial evidence.

## Technical Constraints

- Implement under `axolync-agent/skills-workspace/check-merge-ready` unless later explicitly promoted to a reusable user skill.
- Invocation name: `$check-merge-ready`.
- Accept one PR or a PR group as input.
- Fetch and identify current PR heads before judging.
- Wait for GitHub Actions/checks to finish when requested or when no final status exists yet.
- Distinguish current-head evidence from stale evidence.
- Distinguish GitHub-covered tests from local-only tests.
- Prefer existing repo commands such as `npm run test:github-safe:dry-run`, `npm run test:github-skipped-local:dry-run`, and related builder/report inventory commands when present.
- Do not run full artifact rebuilds unless the user explicitly asks or the merge criterion requires artifact proof.
- Do not merge PRs.
- Do not silently classify unknown evidence as ready.
- Use a deterministic verdict model with at least: `merge-ready`, `not-ready`, `unknown`.

## Proposed Scope

1. Define merge-readiness criteria.
   - GitHub checks are complete and successful for current PR heads.
   - Required local-only tests are run, pass, or are explicitly waived.
   - CRPR evidence is clean, or unresolved findings are listed.
   - Required report/artifact warning gates are zero where relevant.
   - Branch heads and checked evidence match.

2. Add a skill workflow.
   - Parse PR URLs, repo/branch pairs, or a handoff file.
   - Fetch PR metadata.
   - Wait for checks to complete using GitHub CLI where available.
   - Collect local-only dry-run inventories when supported.
   - Run local-only tests only when requested or when the skill is operating in validation mode.
   - Produce a concise Markdown verdict.

3. Add stale-evidence guards.
   - Record each PR head SHA.
   - Reject reports/checks whose embedded identity does not match the PR head.
   - Mark missing or stale evidence as `unknown`, not ready.

4. Add CR evidence handling.
   - Accept CRPR.md paths or PR review state when available.
   - Report unresolved CR findings as blockers.
   - Treat missing CR evidence as unknown unless the user explicitly waives CR.

5. Add output format.
   - Summary verdict.
   - Per repo/PR: branch, SHA, GitHub check result, local-only result, CR result.
   - Blockers and unknowns.
   - Commands run.
   - Evidence paths.

6. Add tests for the decision model.
   - All required evidence green -> `merge-ready`.
   - Any current-head GitHub failure -> `not-ready`.
   - Missing/stale evidence -> `unknown`.
   - Missing CR without waiver -> `unknown`.
   - Local-only failure -> `not-ready`.

## Resolved Decisions

- This skill should block/wait for GitHub Actions when checks are pending.
- This skill should not be satisfied by GitHub alone when local-only tests exist and are required.
- This skill should not merge PRs.
- This skill should not claim merge readiness from stale reports or previous branch heads.
- The first version can be an audit skill with optional validation commands; implementation/fix loops remain separate unless the user asks for a combined workflow.

## Open Questions

- None.
