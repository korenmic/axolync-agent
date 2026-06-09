# Seed 07 - Agent Descriptor-Owned Test Command Exports

## Summary

Remove descriptor fallback warnings for `axolync-agent` build, sanity, and full-test command discovery by publishing those command exports through the repo descriptor.

## Product Context

The add-consumed-repo skill is being updated to produce descriptor-clean repos by default. The agent repo itself should also be descriptor-clean so Builder reports do not rely on legacy test command fallback metadata.

## Technical Constraints

- Keep workspace skill boundary rules intact.
- Do not change the behavior of Sinq handoff skills except where command metadata is described.
- Preserve current test commands and validation scripts.

## Required Outcome

- Builder resolves agent build/sanity/full-test command metadata from the descriptor.
- Agent descriptor fallback warnings disappear from the report.
- The descriptor-standard skill seed remains consistent with agent self-metadata.

## Open Questions

- None.
