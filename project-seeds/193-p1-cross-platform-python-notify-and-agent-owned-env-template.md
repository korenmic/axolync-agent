# Seed 193: Unify notify CLI Into Agent-Owned Cross-Platform `notify.py` + `.env.template`

Priority: P1
Repo: axolync-agent

## Summary

Unify the two divergent notify CLI implementations (`~/bin/notify.ps1` for Windows, `~/bin/notify.sh` for POSIX) into a single cross-platform Python `notify.py` owned by this repo at `skills-user/notify/`, and add a single `.env.template` in the agent repo holding the notify default settings. This makes axolync-agent the owner of the notify implementation, ends the `~/bin`-vs-agent duplication drift, and removes the `~/bin/notify-config.json` dependency. Parked: approved as a seed, not scheduled for implementation yet.

## Product Context

Today the notify CLI is owned by `~/bin` (its own git repo) and resolves through PATH (`notify` -> `notify.cmd` -> `notify.ps1`; plus a separate `notify.sh`). The skill folders carry only instructions, except stale vestigial `notify.ps1` copies: the agent-repo copy is a month behind the live `~/bin` one (Apr 11 vs May 8) — proof the duplication drifts. Cross-platform coverage exists only by maintaining two parallel implementations (`.ps1` + `.sh`) that can and do diverge. The real problem is not "no Mac support"; it is two implementations and two owners for one artifact.

After this seed, the agent repo is the single source of truth: `notify.py` lives in `skills-user/notify/` and installs into userspace as part of the notify skill folder copy (`~/.codex/skills/notify/`, `~/.claude/skills/notify/`) via the deploy flow (seed 194). Both agents run the same script from their own skill copy; copies are overwritten idempotently from the one source on redeploy, so duplication carries no drift risk.

## Technical Constraints

- `notify.py` lives at `skills-user/notify/notify.py`, Python standard library only (Windows/macOS/Linux), preserving the existing positional CLI contract: message, channel or `@name`, taskNumber, duration, botName; bot-name prefixing; ntfy POST to the resolved base URL/channel.
- Installation model: the script ships inside the notify skill folder and is deployed by copying that folder into each agent's userspace skill directory. A thin optional `~/bin` shim (`notify` on PATH delegating to the deployed `notify.py`) may remain for existing callers that invoke the bare `notify` name (e.g. TACTIC notifications); the shim contains no logic.
- Config resolution order, with no `~/bin/notify-config.json` requirement: explicit CLI arg -> process env (`AXOLYNC_NOTIFY_*`) -> nearest ancestor `.env` -> agent-repo `.env.template` defaults -> built-in defaults. Reading a legacy `~/bin/notify-config.json` if present is allowed for back-compat during transition.
- Add a single `.env.template` in the agent repo (root or `bootstrap/`) with `AXOLYNC_NOTIFY_BASE_URL`, `AXOLYNC_NOTIFY_CHANNEL`, `AXOLYNC_NOTIFY_BOT_NAME` defaults matching current builder/browser usage.
- After `notify.py` parity is confirmed, retire `~/bin/notify.ps1` and `~/bin/notify.sh` (and the stale skill-folder `.ps1` copies); `~/bin` stops being an implementation owner.
- Update the notify `SKILL.md` to document `notify.py` as the only implementation.

## Non-Goals

- Retiring the notify `.env` values in other repos (builder/browser). That is a separate future seed once the agent-owned template is the single source of truth.
- Renaming the `AXOLYNC_NOTIFY_*` env prefix to a neutral one.

## Open Questions

- Should the optional `~/bin` PATH shim be kept permanently for the bare `notify` name, or removed once all skill texts invoke the deployed script directly? Recommended: keep the shim; the bare `notify` name is widely referenced in skill instructions.
- Use stdlib `urllib` only for the POST, or allow `requests` if present? Recommended: stdlib `urllib` only, for zero-dependency portability.
