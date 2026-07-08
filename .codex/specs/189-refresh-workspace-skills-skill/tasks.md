# Tasks

- [x] 1. Create the `refresh-workspace-skills` workspace skill
  - Add `skills-workspace/refresh-workspace-skills/SKILL.md`.
  - Use name `refresh-workspace-skills`.
  - Document `$refresh-workspace-skills` as the shortcut.
  - Keep it under `skills-workspace`; do not install it to the user homedir.

- [x] 2. Document safe agent repo update behavior
  - Require locating `axolync-agent`.
  - Require dirty-state refusal before pulling.
  - Require fast-forward-only pull from `origin/master`.
  - Require exact blocker reporting on failure.

- [x] 3. Document workspace skill exposure verification and repair
  - Require locating the current workspace root.
  - Require inspecting `<workspace>/.codex/skills`.
  - Require reporting missing, stale, copied, or incorrectly linked workspace skill exposure.
  - Permit safe repair using existing Axolync bootstrap convention.
  - Forbid overwriting dirty workspace skill files.

- [ ] 4. Document user-homedir and runtime reload boundaries
  - Forbid mutating `~/.codex/skills`.
  - Require comparing visible workspace skills against `axolync-agent/skills-workspace`.
  - Require reporting when current Codex session cannot dynamically reload the skill list.
  - Forbid claiming active-session availability unless it is true.

- [ ] 5. Add validation coverage for the skill
  - Add or update tests/scripts that verify `refresh-workspace-skills` is a valid workspace skill.
  - Assert the skill includes dirty-state refusal, no homedir mutation, workspace exposure verification, and runtime reload caveat.
  - Verify `$lssa` lists the new skill.
