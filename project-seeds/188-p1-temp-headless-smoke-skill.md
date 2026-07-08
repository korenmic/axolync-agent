# 188 - P1 Temporary Headless Smoke Skill

## Summary

Create a workspace skill that gives Codex an explicit, reusable shortcut for running temporary, untracked, headless-browser smoke tests against a non-default local server, then cleaning up the server and reporting exactly what was tested.

Recommended skill name:
- `temp-headless-smoke`

Recommended shortcut:
- `$temp-headless-smoke`

Alternative names considered:
- `headless-smoke`
- `temporary-browser-smoke`
- `ephemeral-headless-test`

## Product Context

Some Axolync UI/runtime changes need quick browser proof before merge, but not every test deserves committed Playwright/Vitest coverage immediately. The user wants a safe workflow that lets Codex run temporary test scripts and a temporary server without taking over the default development port or leaving runtime processes behind.

This skill is permission-scoped and workflow-scoped. It should not introduce durable test files unless the user separately asks for committed test coverage.

## Technical Constraints

- Implement as a workspace skill in `axolync-agent/skills-workspace/temp-headless-smoke`.
- The skill may create untracked temporary automation scripts.
- The skill must infer and design relevant temporary headless smoke tests from the current task, latest agreed design, and suspected risk areas.
- The user does not need to provide exact test scripts, click paths, or assertions unless the behavior is genuinely ambiguous.
- Temporary scripts must stay uncommitted unless the user explicitly asks to keep them.
- The skill must start any local server on a non-default port.
- The skill must not take over the user's default `npm run dev` port.
- The skill must use a headless browser for automation.
- The skill must kill the temporary server before finishing, including on failure where practical.
- The skill must report the tests it performed.
- If testing reveals a bug in the latest agreed design, the skill may fix the bug immediately, rerun the relevant temporary test, and report the fix.
- The skill must not claim merge readiness from temporary tests alone when committed tests or CI are required.
- The skill must respect repo-specific command rules, including RTK when active.

## Proposed Skill Behavior

1. Choose a safe temporary port.
   - Avoid the default dev server port.
   - Prefer an explicit port passed by the user when supplied.
   - Otherwise choose a high-numbered local port and verify it is available.

2. Start the target app/server temporarily.
   - Run the repo's normal dev/start command with the temporary port override.
   - Capture the process id or job handle.
   - Wait until the server is reachable.

3. Create and run temporary headless tests.
   - Infer the relevant temporary smoke coverage from the current feature/bug context.
   - Choose page flows, clicks, assertions, and diagnostics that best prove the latest agreed design.
   - Use an untracked temporary script or inline headless browser automation.
   - Keep the script scoped to the exact manual proof requested.
   - Avoid adding committed test dependencies unless already available.

4. Fix only directly discovered bugs.
   - If the temporary test proves the latest agreed implementation is broken, Codex may patch the relevant code.
   - After the fix, rerun the same temporary proof.
   - Do not expand scope into unrelated cleanup.

5. Clean up.
   - Kill the temporary server.
   - Remove temporary scripts/logs unless the user asks to keep them.
   - Confirm the default dev port was not used.

6. Report.
   - List each temporary test performed.
   - List commands or scripts used.
   - State server port used.
   - State whether any bug was found and fixed.
   - State whether committed tests/CI are still required.

## Suggested `SKILL.md` Core Text

The skill should include the user's authorization in concise operational wording:

> You may create untracked temporary test scripts and run a temporary local server on a non-default port for headless-browser smoke testing. When finished, kill the temporary server and list the tests performed. If these temporary tests expose a bug in the latest agreed design, you may fix it immediately and rerun the relevant test to prove the fix.

The skill should also state:

> Infer and design the relevant temporary headless checks yourself from the current task, latest agreed design, and suspected risk areas. Do not require the user to provide exact scripts or click paths unless the behavior is ambiguous.

## Required Tests / Validation

- Validate skill frontmatter and naming.
- Forward-test the skill on a harmless local static server or mock repo.
- Confirm the forward test uses a non-default port.
- Confirm cleanup kills the temporary server.
- Confirm output lists performed tests.

## Open Questions

None.
