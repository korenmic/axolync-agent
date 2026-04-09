---
name: notify
description: Send concise progress notifications for active work sessions and task completions. Use when the user asks for progress notifications, wants ntfy updates during a run, mentions notify, or when another workflow such as TACTIC needs standardized start, task-done, block, or finish notifications.
---

# Notify

## Overview

Use this skill to prepare the human-readable notification text and send it through the global `notify` CLI.

Treat the CLI as the transport layer with bot-name prefix support. Compose the message body in the agent, let the CLI resolve/prefix the bot name, and then call `notify` to deliver it.

## Resolve The Defaults

Resolve notification settings in this order:

1. Explicit CLI channel argument or bot-name argument
2. `AXOLYNC_NOTIFY_*` values from the current process or workspace `.env`
3. `~/bin/notify-config.json`

Recognized settings:

- `AXOLYNC_NOTIFY_BASE_URL`
- `AXOLYNC_NOTIFY_CHANNEL`
- `AXOLYNC_NOTIFY_BOT_NAME`

Default global config path:

- `~/bin/notify-config.json`

Default config shape:

```json
{
  "baseUrl": "https://ntfy.sh",
  "channel": "miki800_done",
  "botName": "Codex"
}
```

Use `Codex` when no bot name override is present.

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

Send notifications with the global CLI on `PATH`:

```powershell
notify "<message body>" [channel] [taskNumber] [duration] [botName]
```

Notes:

- The CLI accepts the builder-compatible positional shape.
- The channel argument is optional and overrides the configured/default channel.
- `taskNumber` and `duration` are compatibility helpers; prefer putting the final session summary into the message itself.
- The optional `botName` argument overrides env/config/default bot naming for that one notification.
- For the shortest custom-name override, you may pass `@Name` as the second argument instead of a channel, for example `notify "<message body>" @Sinq2`.
- The CLI looks upward for the nearest `.env`, so a workspace-level `.env` can provide a default bot name across nested repos.

## Default Events

When paired with `TACTIC`, send:

- `start`
- after each completed task
- `block` when runnable work is exhausted but blockers remain
- `finish`

Use additional notifications only when they materially improve visibility.
