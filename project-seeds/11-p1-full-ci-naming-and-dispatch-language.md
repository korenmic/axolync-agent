# Full CI Naming And Dispatch Language

## Summary

Update agent-facing guidance so future agents use `full-ci` for maximal validation and `full-ci-core` for the reduced core-only Builder suite.

## Product Context

Builder is splitting the old core-focused `full-ci` behavior into `full-ci-core` and reserving `full-ci` for maximal descriptor-aware validation. Agent prompts, skills, and handoff language must not keep using the old ambiguous meaning.

The goal is to prevent future Sinq/manual dispatch workflows from calling a core-only run "full" merge proof.

## Technical Constraints

- Priority: P1.
- Scope is `axolync-agent`.
- Do not create or modify user-global skills.
- Do not use Sinq dispatch for validation.
- This seed may be implemented independently of Builder code, but final wording should align with Builder's implemented command names.
- Keep guidance generic: Builder owns the command implementation; agent docs own the language and request discipline.

## Required Behavior

- Agent-facing docs must state that `full-ci` means maximal descriptor-aware validation.
- Agent-facing docs must state that `full-ci-core` means reduced/core-only validation.
- Any skill or prompt template that asks for the old core-only behavior must use `full-ci-core`.
- Any merge-proof/nightly/maximal validation language must use `full-ci`.
- Guidance must explicitly reject report-only, no-ci, dry-run, or core-only runs as substitutes for maximal full-CI proof.
- Guidance must preserve the rule that implementation agents should not use Sinq dispatch unless the user explicitly authorizes it.

## Open Questions

None. If Builder command names change during implementation, align wording to the final Builder names before merging.
