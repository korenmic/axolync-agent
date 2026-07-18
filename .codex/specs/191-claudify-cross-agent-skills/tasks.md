# Tasks - Claudify Cross-Agent Skills

Derived from `requirements.md` and `design.md` in this spec folder.

- [x] 1. Add `scripts/claudify.py` with the known-skill scoped transform, bucket generation, gitignored output, workspace auto-install, and the user-skill install offer.
- [x] 2. Add `.claudify-out/` to `.gitignore`.
- [x] 3. Add `tests/test_claudify.py` covering no-over-reach, active conversion, non-skill `$` preservation, full skill coverage, and the source `/name` guardrail.
- [x] 4. Add `.github/workflows/claudify.yml` running the claudify tests in `axolync-agent` CI.
- [x] 5. Add the `claudify` workspace skill (`skills-workspace/claudify/SKILL.md`) that runs the script and echoes the user-skill install offer.
- [x] 6. Add cross-agent (Codex vs Claude) branching to the skills sections of `README.md` and the bootstrap docs.
- [x] 7. Verify: run claudify against the real sources and confirm generated output, workspace install, and the printed user-skill offer; run the test suite green.
- [x] 8. Add rogue-invocation escaping (`/name` -> `/ name`, invocation-position only, run before `$name` conversion) with a reversible transform, plus escape and path-safety tests.
- [x] 9. Add the per-file uninventoried `$`-candidate allowlist and a CI test that fails on any unexpected uninventoried candidate.
