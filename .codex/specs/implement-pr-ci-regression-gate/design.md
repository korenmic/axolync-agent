# Design

## Overview

The `$implement` user skill remains a workflow wrapper over `$tactic` and `$notify`. This change adds a documented PR CI regression gate after the push phase for PR-targeted implementation sessions.

The gate is not a CI runner. It is a handoff policy and deterministic decision model:

1. capture baseline check state when practical
2. push the completed implementation branch
3. wait for GitHub checks on the pushed PR head when a PR is known
4. classify the result as pass, PR-caused regression, pre-existing/unrelated failure, or unknown
5. block a ready/push-complete handoff when PR-caused regressions remain

## Skill Flow Integration

Existing `$implement` flow:

1. resolve workspace and queue
2. warn on dirty worktrees
3. invoke `$tactic`
4. preserve TACTIC task/commit/blocker discipline
5. push committed work
6. notify push completion

New PR-targeted flow:

1. perform the same existing steps through push
2. if the push target is a PR branch or a PR is explicitly known, run the PR CI regression gate
3. if the gate passes, send the normal completion handoff
4. if the gate finds PR-caused failures, report blockers and keep the PR in implementation responsibility
5. if the gate is unknown or unavailable, report the uncertainty instead of claiming GitHub CI success

## Decision Model

Add small pure-Python helper structures to `skills-user/implement/scripts/implement_tasks.py`:

- `CheckSnapshot`: immutable check name plus conclusion
- `PrCiGateResult`: status, blocker names, and explanatory message
- `classify_pr_ci_gate`: compares optional baseline checks with post-push checks
- `format_pr_ci_gate_result`: formats a concise handoff-safe message

Gate statuses:

- `pass`: every known post-push check is successful or neutral
- `pr-regression`: one or more checks that previously passed now fail
- `pre-existing-failure`: failing checks existed in the baseline and are not newly introduced
- `unknown`: post-push check data is missing or a PR/check result cannot be observed

The helper deliberately does not call `gh`; command execution remains a runtime/operator responsibility. The helper only makes classification testable.

## Documentation Changes

Update `skills-user/implement/SKILL.md`:

- add PR CI gate to the high-level flow
- document the baseline and post-push check phases
- document that PR-caused failures remain in scope for `$implement`
- document that unavailable checks are reported as unknown
- extend authority boundaries so `$implement` owns final PR CI handoff validation

## Testing

Extend `tests/test_implement.py` with deterministic unit tests for:

- non-PR push behavior remains unaffected
- all passing post-push checks produce a pass result
- passed-to-failed check transition produces a PR regression blocker
- already failing baseline check is classified as pre-existing
- missing post-push data is classified as unknown
- formatted output includes blocker/check names

## Self-Review Notes

- The design does not make `$implement` re-run CI locally.
- The design does not replace `$tactic`.
- The design does not require GitHub checks for non-PR local work.
- The design prevents a PR-caused GitHub red check from being silently handed back as done.
