---
name: notify
description: Send concise progress notifications for active work sessions and task completions. Use when the user asks for progress notifications, wants ntfy updates during a run, mentions notify, or when another workflow such as TACTIC needs standardized start, task-done, block, or finish notifications.
---

# Notify

## Overview

Use this skill to prepare the human-readable notification text and send it through the bundled cross-platform CLI, `notify.py` — the only notify implementation. It ships inside this skill folder and runs anywhere Python 3 runs.

Treat the CLI as the transport layer with bot-name prefix support. Compose the message body in the agent, let the CLI resolve/prefix the bot name, and invoke it via the composed per-agent path (see Use The CLI).

## Resolve The Defaults

Resolve notification settings in this order:

1. Explicit CLI channel argument or bot-name argument
2. `AXOLYNC_NOTIFY_*` values from the current process environment
3. The nearest ancestor `.env` that actually defines the specific notify setting being resolved
4. Legacy `notify-config.json` (the skill/script directory first, then `~/bin/notify-config.json`, back-compat only)
5. The agent repo root `.env.template` defaults
6. Built-in defaults (`https://ntfy.sh`, bot `Codex`)

Recognized settings:

- `AXOLYNC_NOTIFY_BASE_URL`
- `AXOLYNC_NOTIFY_CHANNEL`
- `AXOLYNC_NOTIFY_BOT_NAME`

Each setting is resolved independently. A nearer `.env` that does not define `AXOLYNC_NOTIFY_BOT_NAME` must not block a higher ancestor `.env` that does define it.

Example:

- repo `.env` contains only build variables
- workspace root `.env` contains `AXOLYNC_NOTIFY_BOT_NAME=Sinq4`
- running `notify` inside the repo should still send as `Sinq4`

The agent-owned defaults live in the agent repo root `.env.template` (base URL, channel, bot name). Copy it to a `.env` at a workspace or repo root to override; never edit the template per-machine. Use `Codex` when no bot name override is present.

## Compose Messages

Keep messages short and single-purpose.

Default TACTIC-oriented body format:

```text
out of total X tasks - [D done / C current / R remaining]; last task <duration>, session <duration> - <optional short note>
```

Rules:

- Keep the optional note under one short sentence.
- Prefer `n/a` for last task duration on session start.
- Keep block notifications explicit about what is waiting on user input.
- Avoid dumping logs or stack traces into the notification body.
- Prefer sending the body without a manual `Name:` prefix; the CLI adds the resolved bot name.
- If an older caller already passes a prefixed message, the CLI avoids duplicating the prefix.

## Use The CLI

Resolve the running agent's home via the `$agent-home` skill, then invoke the deployed script by full path — there is no PATH-name dependency and no `~/bin` involvement:

```text
python <agent-home>/skills/notify/notify.py "<message body>" [channel] [taskNumber] [duration] [botName]
```

(`<agent-home>` is `~/.codex` under Codex and `~/.claude` under Claude. When working inside the agent repo itself, `skills-user/notify/notify.py` is the same script.)

Notes:

- The CLI accepts the builder-compatible positional shape.
- The channel argument is optional and overrides the configured/default channel.
- `taskNumber` and `duration` are compatibility helpers; prefer putting the final session summary into the message itself.
- The optional `botName` argument overrides env/config/default bot naming for that one notification.
- For the shortest custom-name override, you may pass `@Name` as the second argument instead of a channel, for example `python <agent-home>/skills/notify/notify.py "<message body>" @Sinq2`.
- The CLI resolves each notify setting from the nearest ancestor `.env` that actually defines that setting, so a workspace-level `.env` can still provide `AXOLYNC_NOTIFY_BOT_NAME` when a nested repo `.env` exists but does not define notify settings.

## Default Events

When paired with `TACTIC`, send:

- `start`
- after each completed task
- `block` when runnable work is exhausted but blockers remain
- `finish`

Use additional notifications only when they materially improve visibility.
