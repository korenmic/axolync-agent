---
name: temp-headless-smoke
description: "Run temporary, untracked headless-browser smoke tests against a non-default local server, infer relevant checks from the current feature or bug context, clean up the temporary server/scripts, and report tests performed. Use when invoked as $temp-headless-smoke or when the user authorizes temporary headless smoke validation."
---

# Temporary Headless Smoke

Use this workspace skill when the user authorizes temporary headless browser smoke testing for an Axolync feature, bug fix, or PR branch.

This skill is a workspace-only testing workflow. Do not install or copy it into `~/.codex/skills`.

## Shortcut

Use `$temp-headless-smoke` as the canonical shortcut.

## Test Design Responsibility

Infer and design the relevant temporary headless checks yourself from:

- the current task
- the latest agreed design
- the suspected risk areas
- the visible UI or runtime behavior being validated

Do not require the user to provide exact scripts, click paths, or assertions unless the behavior is genuinely ambiguous. Choose the page flows, clicks, waits, assertions, and diagnostics that best prove or disprove the current design.

Keep temporary smoke coverage scoped to the current proof target. Do not expand into broad exploratory testing unless the user explicitly asks.
