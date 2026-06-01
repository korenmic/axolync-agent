# Nightly CI Safe Full-CI Enforcement

## Summary

Update the agent-owned `$nightly-ci-safe` workflow so it cannot satisfy a full nightly request with report-only, no-ci, dry-run, sanity, GitHub-only, reused stale, or mostly `not_run` evidence.

The workflow must call builder's canonical `full-ci` path for the one allowed full inventory pass, then verify builder's full-CI proof gate before declaring success.

## Priority

- `P0`

## Product Context

The nightly-safe skill was meant to prevent uncontrolled repeated full-CI reruns. It was not meant to downgrade full nightly validation into report-only or sanity evidence.

Recent handoffs showed a real process gap:

- reports were mirrored with many inventory placeholders and only a few actual pass/fail rows;
- those reports were summarized as if they were full nightly evidence;
- the user expected a May-19-scale full test proof, not a reduced sanity/dry-run report.

The agent workflow must preserve the cost-control purpose of `$nightly-ci-safe` while enforcing the evidence standard.

## Technical Constraints

- Implement in `axolync-agent`.
- Update the tracked `nightly-ci-safe` skill and any helper docs/scripts it uses.
- Do not make the skill invent its own definition of full CI; it must defer to builder's canonical `full-ci` command/proof gate.
- Do not allow substitutions:
  - `report:generate`
  - `report:noci`
  - `report:generate:dry`
  - `sanity`
  - short smoke checks
  - GitHub-only report data
  - stale reused local evidence
- Keep the existing safety rule: run full CI at most once per nightly session.
- The implementation proof for this seed should not require running the full multi-hour suite. It should verify that the skill would call builder `full-ci` and that it can consume builder's candidate inventory/proof output.
- The skill must report clearly when full nightly validation did not complete.

## Proposed Scope

1. Update `$nightly-ci-safe` instructions.
   - The one allowed full inventory pass must be builder `full-ci`.
   - The skill must not call report-only/no-ci/dry-run/sanity commands as substitutes.
   - If builder `full-ci` is unavailable or blocked, report `full nightly not completed`.

2. Add proof-gate verification to the skill.
   - After the builder run, inspect builder's full-CI proof status.
   - Require executed full-CI proof for real success.
   - For implementation/testing of the skill itself, allow a clearly labeled candidate-inventory proof mode that does not claim executed success.

3. Add final checklist output.
   - Command used.
   - Builder run preset used.
   - Full-CI proof status.
   - Executed test count.
   - Not-run count.
   - Browser full-CI candidate/executed status.
   - Builder full-CI candidate/executed status.
   - Artifact build/mirror status when requested.
   - Any blockers.

4. Add dispatch guard language.
   - Incoming dispatches that explicitly request `$nightly-ci-safe`, `nightly ci safe`, or full nightly validation must preserve the full-CI requirement.
   - Time pressure does not permit substituting report-only/no-ci/sanity.
   - If a requester asks for short validation, use sanity; if they ask for nightly-safe, use full-ci.

5. Add tests or static validation.
   - Skill text includes the forbidden substitution list.
   - Skill text points to builder `full-ci`.
   - Skill text requires proof-gate verification before success.
   - Candidate-inventory proof mode is labeled as non-executed and cannot be summarized as a passed full nightly.

## Definition Of Done

This seed is complete when:

1. `$nightly-ci-safe` explicitly calls builder `full-ci` for full nightly validation.
2. `$nightly-ci-safe` forbids report-only/no-ci/dry-run/sanity substitution.
3. `$nightly-ci-safe` verifies builder's full-CI proof gate before declaring success.
4. `$nightly-ci-safe` reports `full nightly not completed` when full-ci is unavailable, blocked, or only candidate-inventory proof exists.
5. `$nightly-ci-safe` emits a final checklist with executed/not-run counts and key repo proof statuses.
6. Dispatch guard language preserves the full-CI requirement under time pressure.
7. Implementation verification uses builder's candidate inventory/proof mode rather than running a multi-hour full-CI execution.
8. The verification would catch the prior bad state where nightly-safe evidence had only hundreds of candidates or mostly `not_run` rows instead of the expected full candidate scale.

## Resolved Decisions

- Agent workflow policy belongs in `axolync-agent`; builder execution semantics belong in `axolync-builder`.
- `$nightly-ci-safe` remains a cost-control workflow, not a permission to downgrade validation.
- Candidate-inventory proof is acceptable for implementation acceptance, but not as a claim that full nightly execution passed.

## Open Questions

1. Should the skill invoke builder `full-ci` directly, or through a small agent helper that also parses the proof gate and formats the checklist?
2. Should the skill require artifact build/mirror after full-ci by default, or only when the dispatch explicitly asks for artifacts?
