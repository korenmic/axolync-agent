# Tasks

- [ ] 1. Create the `temp-headless-smoke` workspace skill
  - Add `skills-workspace/temp-headless-smoke/SKILL.md`.
  - Use name `temp-headless-smoke`.
  - Document `$temp-headless-smoke` as the shortcut.
  - Keep it under `skills-workspace`; do not install it to the user homedir.

- [ ] 2. Document runner-owned temporary headless test design
  - State that the agent must infer relevant tests from current task context, latest agreed design, and suspected risks.
  - State that the user does not need to provide exact scripts or click paths unless behavior is ambiguous.
  - Require tests to stay scoped to the current proof target.

- [ ] 3. Document temporary server and script hygiene
  - Require a non-default temporary port.
  - Require tracking and killing the temporary server.
  - Require temporary scripts/logs to stay untracked and be removed unless the user asks to keep them.
  - Require reporting the temporary port and tests performed.

- [ ] 4. Document scoped bug fix and retest behavior
  - Authorize immediate scoped fixes when temporary tests prove a bug in the latest agreed design.
  - Require rerunning the relevant temporary test after the fix.
  - Warn against unrelated cleanup or behavior expansion.
  - Warn that temporary smoke tests do not replace committed tests, CI, or rebuild gates.

- [ ] 5. Add validation coverage for the skill
  - Add or update tests/scripts that verify `temp-headless-smoke` is a valid workspace skill.
  - Assert the skill includes non-default port, cleanup, runner-owned test design, and report requirements.
  - Verify `$lssa` lists the new skill.

