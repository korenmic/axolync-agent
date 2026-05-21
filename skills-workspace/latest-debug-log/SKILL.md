---
name: latest-debug-log
description: Find the newest Axolync Android/browser debug ZIP in the current user's Downloads folder. Use when invoked as $latest-debug-log or when the user asks to inspect the latest axolync-debug-*.zip.
---

# Latest Debug Log

Use this skill to locate the newest Axolync debug ZIP available under the current user's Downloads folder.

## Workflow

Run the bundled Python helper from the `axolync-agent` repo root:

```powershell
py skills-workspace/latest-debug-log/scripts/latest_debug_log.py
```

If `py` is unavailable, run the same script with `python`.

The helper searches:

```text
~/Downloads/axolync-debug-*.zip
```

It selects the newest file by filesystem modification time at the moment the skill is run, then prints:

- full path
- size
- modified timestamp
- ZIP entry count
- a short entry preview

## Using The Result

Use the returned path as the debug ZIP source for the current task. Do not assume the previous latest path is still current; rerun the helper each time the skill is invoked.

If no matching ZIP exists, report that no `axolync-debug-*.zip` file was found in `~/Downloads`.

## Guardrails

- Do not mutate, move, or delete the debug ZIP.
- Do not extract the ZIP unless the user task requires deeper inspection.
- If extracting is needed, use a task-local temporary directory, not the Downloads folder.
