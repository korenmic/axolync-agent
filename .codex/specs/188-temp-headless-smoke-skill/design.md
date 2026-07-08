# Design

## Overview

`temp-headless-smoke` is a workspace skill for controlled, temporary runtime smoke testing. It is not a committed test framework. It gives agents permission and rules for creating untracked headless-browser automation against a temporary non-default local server, then cleaning up and reporting evidence.

## Skill Location

Create:

```text
skills-workspace/temp-headless-smoke/SKILL.md
```

No scripts are required for v1. The workflow can be instruction-only because server commands and browser automation tools vary by repo and task.

## Triggering

Frontmatter:

```yaml
name: temp-headless-smoke
description: Run temporary, untracked headless-browser smoke tests against a non-default local server, infer relevant checks from the current feature or bug context, clean up the temporary server/scripts, and report tests performed. Use when invoked as $temp-headless-smoke or when the user authorizes temporary headless smoke validation.
```

## Workflow

The skill directs agents to:

1. infer tests from the current task and risk areas
2. pick a non-default temporary port
3. start a temporary server with a trackable process handle
4. run headless browser automation through available tools or temporary scripts
5. fix and rerun if the smoke test proves a scoped bug
6. kill the temporary server and delete temporary artifacts
7. report tests, port, bugs, fixes, and remaining merge gates

## Guardrails

- Never take over the user's default dev server port.
- Never leave the temporary server running.
- Never commit temporary scripts without explicit user approval.
- Do not use temporary smoke tests as a replacement for CI or committed regression tests when those are required.
- Respect RTK/AGENTS command rules whenever active.

## Validation

The implementation is primarily docs/skill validation. `$lssa` must list the new workspace skill after implementation. A lightweight content test can assert required phrases in `SKILL.md` so future edits do not remove the key authorization and cleanup rules.

