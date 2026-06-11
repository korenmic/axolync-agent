# Tasks

- [x] 1. Document the `$implement` PR CI regression gate
  - Update `skills-user/implement/SKILL.md`.
  - Add the gate after push and before completion handoff.
  - State that the gate applies to PR-targeted implementation sessions.
  - State that unavailable GitHub checks must be reported as unknown instead of success.
  - Preserve TACTIC and notify authority boundaries.

- [x] 2. Add deterministic PR CI gate helpers
  - Update `skills-user/implement/scripts/implement_tasks.py`.
  - Add immutable check snapshot/result structures.
  - Add classification logic for pass, PR-caused regression, pre-existing/unrelated failure, and unknown.
  - Add formatting logic that keeps blocker details visible.
  - Keep helper logic free of live GitHub calls.

- [x] 3. Add regression tests for PR CI gate classification
  - Update `tests/test_implement.py`.
  - Cover all passing checks.
  - Cover passed-to-failed regression.
  - Cover already failing baseline checks.
  - Cover unavailable/unknown check data.
  - Cover formatted blocker output.

- [x] 4. Verify implement skill tests
  - Run `python -m unittest tests.test_implement -v`.
  - Run `python -m unittest tests.test_queue_status tests.test_enqueue tests.test_implement -v`.
  - Fix any regressions caused by the PR CI gate changes.

- [x] 5. Self-review and push to master
  - Confirm the seed/spec/tasks are committed.
  - Confirm the skill docs match the approved behavior.
  - Confirm implementation is on `axolync-agent` master.
  - Push to `origin/master`.
