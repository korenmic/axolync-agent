# Consumed Repo GitHub-Safe Workflow Contract

## Summary

Update the `axolync-add-consumed-repo` workspace skill so future Axolync repos are scaffolded/reviewed with the GitHub-safe workflow contract expected by Builder's mixed GitHub/local CI proof model.

## Product Context

Builder is moving toward a split proof model: GitHub Actions run `github-safe` tests for each repo, while local/nightly runs cover `github-skipped-local` tests. New consumed repos must not require later cleanup PRs just to expose a compatible workflow entrypoint.

## Technical Constraints

- Priority: P1.
- Scope is `axolync-agent`.
- Do not create user-global skills.
- Keep workflow requirements generic enough for repos with zero tests.
- Preserve the skill's existing descriptor-first onboarding guidance.

## Required Behavior

- The skill checklist must mention compatible `push`, `pull_request`, and `workflow_dispatch` entrypoints.
- The skill must require parseable test output or an explicit no-tests/zero-candidate declaration.
- The skill must remind agents that Builder orchestrates multiple repo-local GitHub Actions runs; one repo's workflow should not clone/test all other repos.
- The skill must mention exact-HEAD proof and stale-run rejection.
- The skill must document that split full-CI proof is an explicit Builder mode: GitHub-safe proof may run in GitHub while GitHub-skipped-local proof runs locally.
- Agent-facing guidance must not allow report-only, no-ci, dry-run, or sanity evidence to be called split full-CI proof.
- If GitHub cloud proof fails and Builder falls back locally, agents must keep that fallback visible instead of calling it clean cloud success.

## Open Questions

- None.
