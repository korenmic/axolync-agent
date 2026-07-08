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

## Temporary Server And File Hygiene

When a browser app server is needed, start a temporary server on a non-default port. Do not take over the user's normal development port.

Track the temporary server process you start and terminate it before finishing the turn. If process cleanup fails, report the PID, port, and attempted cleanup command.

Keep any throwaway headless scripts, screenshots, logs, and scratch data untracked. Remove them before finishing unless the user explicitly asks to keep a specific artifact.

When reporting results, include:

- the temporary port used
- each temporary headless test performed
- whether temporary scripts or logs were removed
- whether the temporary server was killed
