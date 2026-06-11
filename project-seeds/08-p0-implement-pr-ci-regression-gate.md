# Implement PR CI Regression Gate

## Summary

Harden the `$implement` user skill so PR-targeted implementation sessions do not finish while newly pushed PR checks are red. When `$implement` pushes to a PR branch, it should inspect the relevant GitHub check baseline when possible, wait for the pushed PR head checks to finish, compare the post-push status against the baseline, and treat PR-caused regressions as part of the implementer's delivery responsibility.

The immediate motivation is a PR that locally passed focused checks but introduced a GitHub CI failure after push. `$implement` should make that failure mode harder to hand back as "done".

## Product Context

Axolync implementation sessions often end by pushing a branch or PR and notifying the user. A local focused test set is useful but not always identical to GitHub CI. When a PR is part of the delivery contract, a green handoff should include the remote checks that GitHub actually runs for that PR.

The desired policy is:

1. Before pushing a PR-targeted branch, capture the current check baseline if it is available.
2. After pushing, wait for GitHub checks on the new PR head to complete.
3. If a check that was previously passing now fails and the failure is caused by the pushed PR, the implementer owns the fix.
4. If the failure is unrelated, environmental, or pre-existing, report that clearly instead of claiming merge readiness.

This should keep `$implement` as a workflow skill, not a CI engine. It should document the required behavior and expose small helper logic that can be tested without contacting GitHub.

## Technical Constraints

- Implement under `axolync-agent/skills-user/implement`.
- Keep `$implement` a thin wrapper around `$tactic` and `$notify`; do not replace TACTIC.
- Apply the new CI gate only when the implementation session pushes to a PR-targeted branch or otherwise identifies a PR.
- Do not require GitHub CI for local-only, no-push, or master-only work unless the user explicitly requested it.
- Use GitHub CLI status/check concepts in the skill documentation, but keep helper code deterministic and unit-testable.
- Baseline inspection is best-effort: lack of a readable baseline should not hide post-push PR failures.
- Post-push check waiting must produce one of: pass, PR-caused failure, non-PR/environment/pre-existing failure, unavailable/unknown.
- If PR-caused failures remain, `$implement` must not send a successful push-complete/ready notification.
- Preserve existing branch-selection, dirty-worktree warning, push, and notify behavior.
- Add tests for the new decision model.

## Proposed Scope

1. Document the PR CI regression gate in the `$implement` skill.
   - Explain when it applies.
   - Explain the baseline and post-push check phases.
   - Explain that PR-caused failures remain in scope for the implement session.
   - Explain how unavailable checks should be reported.

2. Add deterministic helper objects/functions for PR CI gate decisions.
   - Represent baseline check conclusions.
   - Represent post-push check conclusions.
   - Classify the gate as pass, PR-caused failure, pre-existing/unrelated failure, or unknown.
   - Expose formatting suitable for a handoff message.

3. Update the `$implement` flow documentation.
   - Insert the PR CI gate after push and before push-complete/ready handoff.
   - Require a failed gate to report blocker details instead of claiming done.
   - Preserve the existing rule that `$tactic` owns implementation and `$implement` owns wrapper/push/handoff.

4. Add tests.
   - Existing non-PR push behavior remains unchanged.
   - A PR with all post-push checks passing passes the gate.
   - A previously passing check now failing is classified as a PR-caused regression.
   - A check already failing before push is classified as pre-existing unless evidence marks it PR-caused.
   - Unknown/unavailable check state is reported explicitly and does not masquerade as success.

## Resolved Decisions

- The PR CI gate applies to PR-targeted `$implement` sessions, not every local implementation.
- Baseline lookup is best-effort, but post-push failures cannot be ignored.
- `$implement` should wait for GitHub checks after pushing a PR branch when possible.
- If the PR introduces a GitHub failure, fixing it is part of the delivery responsibility.
- This seed does not add a full GitHub API runner. It hardens skill instructions and unit-testable decision helpers so future executions follow the policy.

## Open Questions

- None.
