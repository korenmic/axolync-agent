---
name: agent-home
description: Resolve and output the running agent's home directory (~/.codex for Codex, ~/.claude for Claude) as a reusable primitive for any skill needing per-agent paths. Use when invoked as $agent-home or when a skill or user needs the current agent's skill/home root.
---

# Agent Home

Generic read-only primitive: resolve the home directory of the agent that is currently running, so other skills can compose per-agent paths without hardcoding either agent.

## Resolve

- Codex session -> `~/.codex`
- Claude session -> `~/.claude`

The running agent knows what it is; do not ask the user. Output the absolute path (expanded, OS-native separators). Perform no writes and no directory creation.

## Composition

Consumers append well-known subpaths under the resolved home. Canonical example — invoking the notify CLI:

```text
python <agent-home>/skills/notify/notify.py "<message>" [channel|@botName] [taskNumber] [duration] [botName]
```

Other valid compositions include `<agent-home>/skills/<skill>/...` for any deployed userspace skill asset.

## Rules

- Read-only: never create, junction, or modify anything under the resolved path.
- If the resolved directory does not exist, report that plainly instead of guessing an alternative.
- This skill resolves the USER-level agent home, not workspace-local `.codex`/`.claude` folders.
