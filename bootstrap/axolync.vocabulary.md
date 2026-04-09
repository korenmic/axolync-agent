# Axolync Vocabulary

This file is the builder-side glossary for Axolync.

For builder-owned preset TOML language, CLI selection, and output-side copied TOML behavior, also read [config/build-presets/README.md](config/build-presets/README.md).

Purpose:
- give humans and coding agents one place to resolve project-specific wording
- reduce drift in how concepts are named across builder, browser, Android, and plugin repos
- define preferred terms when older chat wording or temporary wording is ambiguous

This file is not a quick-start guide. Use [README.md](README.md) for commands, build/deploy flow, and output layout.

## How To Use This File

- Prefer the **Preferred term** in new docs, reports, seeds, specs, and code comments.
- Treat **Aliases / older wording** as historical language that may still appear in older chat logs or files.
- If a term is still unsettled, it is marked as **provisional**.
- If a repo-specific implementation differs from the shared concept, the shared concept still belongs here and the implementation detail belongs in that repo's own docs.

## Core Product Terms

### Axolync
- **Meaning:** The overall karaoke/lyrics synchronization product and repo family.
- **Use when:** Referring to the system as a whole rather than one repo.

### Browser
- **Meaning:** The web application repo and runtime UI layer.
- **Repo:** `axolync-browser`
- **Includes:** visible UI, runtime state, addon selection, rendering, debug panel.

### Android Wrapper
- **Meaning:** The Android host app that packages and serves the browser bundle and exposes Android-native capabilities.
- **Repo:** `axolync-android-wrapper`

### Builder
- **Meaning:** The orchestration repo that builds, validates, inventories, reports, and mirrors artifacts across repos.
- **Repo:** `axolync-builder`

### Plugins Contract
- **Meaning:** The cross-repo contract/schema authority for plugin-facing structured interfaces.
- **Repo:** `axolync-plugins-contract`

## Plugin Stack Terms

### Bridge Plugin
- **Preferred term:** `plugin`
- **Meaning:** A wrapper bridge plugin in ecosystems such as Capacitor, Electron, or Tauri.
- **Use when:** Referring to the JS-to-native bridge surface rather than the installable Axolync package.
- **Examples:** a Capacitor plugin, an Electron bridge plugin, a Tauri plugin.

### Addon
- **Preferred term:** `addon`
- **Aliases / older wording:** `plugin` (legacy Axolync meaning)
- **Meaning:** The installable Axolync package/container that ships adapter logic and metadata.
- **Examples:** `songsense-bridge`, `syncengine-bridge`, `lyricflow-bridge`, deterministic demo addons.

### Addon Bundle
- **Preferred term:** `addon bundle`
- **Aliases / older wording:** `plugin bundle`, `plugin zip`, `.zip package of installable plugin`, `plugin package`
- **Meaning:** The installable `.zip` artifact shipped for an addon.
- **Why this term:** `bundle` is short and does not over-assume runtime behavior.

### Adapter
- **Preferred term:** `adapter`
- **Meaning:** A provider-facing implementation entry inside an addon.
- **Examples:** `lrclib`, `shazam-statusbar`, `fake-json`, `shazam.py`, `node-shazam-api`.

### Provider
- **Preferred term:** `provider`
- **Meaning:** The external service, data source, local tool, or recognition backend an adapter talks to.

### Demo Addon
- **Preferred term:** `demo addon`
- **Aliases / older wording:** `demo plugin`
- **Meaning:** An addon whose purpose is deterministic local demo/test behavior rather than live production behavior.

### Demo Adapter
- **Preferred term:** `demo adapter`
- **Meaning:** An adapter intended for deterministic local/demo behavior.

### Demo Flow
- **Preferred term:** `demo flow`
- **Meaning:** A browser/runtime path that intentionally uses deterministic demo addons, demo songs, or demo timing logic.

### Demo Song File
- **Preferred term:** `demo song file`
- **Meaning:** A fixed local media asset used for demo playback.

## Main Runtime Plugins

### SongSense
- **Preferred term:** `SongSense`
- **Meaning:** The detection controller layer that identifies what song is currently playing.

### SyncEngine
- **Preferred term:** `SyncEngine`
- **Meaning:** The timing-alignment controller layer that computes offset/rate-like synchronization parameters.

### LyricFlow
- **Preferred term:** `LyricFlow`
- **Meaning:** The lyric retrieval and lyric-unit shaping controller layer.

## Host / Execution Terms

### Bridged
- **Preferred term:** `bridged`
- **Meaning:** A host mode where the runtime reaches backend logic through an intermediate service boundary, usually HTTP.
- **Examples:** desktop browser -> local HTTP bridge -> Python host.

### Unbridged
- **Preferred term:** `unbridged`
- **Meaning:** A host mode where runtime logic is executed directly inside the host environment without a separate backend process/service boundary.
- **Examples:** embedded Python on Android; possible future unbridged TypeScript plugin execution.

### Embedded Python
- **Preferred term:** `embedded Python`
- **Meaning:** CPython loaded inside the host process rather than launched as a separate Python process.
- **Current strongest example:** Android via Chaquopy.

### Host Mode
- **Preferred term:** `host mode`
- **Meaning:** The policy that determines how runtime code reaches addon or backend logic.
- **Examples:** `bridged-http`, `embedded-python`, future modes if introduced.

### Local HTTP Bridge
- **Preferred term:** `local HTTP bridge`
- **Meaning:** A local HTTP compatibility boundary used by the runtime to reach backend logic.
- **Important distinction:** On Android this may still be an app-local route even when the backend logic is embedded rather than a separate process.

## Reporting / Builder Terms

### Report
- **Preferred term:** `report`
- **Meaning:** The generated builder HTML/JSON artifact set under `artifacts/output/`.

### Artifact
- **Preferred term:** `artifact`
- **Meaning:** Any generated build output, report output, mirror output, package, APK, bundle, or metadata file.

### Artifact Inventory
- **Preferred term:** `artifact inventory`
- **Meaning:** The structured list of generated artifacts discovered and rendered in builder outputs.

### Inventory
- **Preferred term:** `inventory`
- **Meaning:** A discovered structured listing of existing items, whether or not they were executed or shipped.
- **Common uses:** test inventory, adapter inventory, repo inventory, seed inventory, artifact inventory.

### Dry Run
- **Preferred term:** `dry run`
- **Meaning:** A non-mutating planning or mock-execution path that collects/report state without executing the full real pipeline.

### Wet Run
- **Preferred term:** `wet run`
- **Meaning:** A real execution path that runs concrete build/test/report work.
- **Note:** This term is understood internally but less standard outside the project.

### Feature Seed
- **Preferred term:** `feature seed`
- **Aliases / older wording:** `seed`
- **Meaning:** A pre-spec concept document that captures a future feature, investigation direction, or architecture idea.

### Presentation
- **Preferred term:** `presentation`
- **Meaning:** A companion HTML artifact for a seed or investigation, intended to explain the concept visually and quickly.

### Spec Maker
- **Preferred term:** `spec maker`
- **Meaning:** The workflow that turns a seed/feature idea into `requirements.md`, `design.md`, and `tasks.md`.

### Workflow
- **Preferred term:** `workflow`
- **Meaning:** The committed project procedure for how specs, tasks, commits, testing, notifications, and reports are handled.

### Notify
- **Preferred term:** `notify`
- **Meaning:** The explicit task/build completion signaling path, currently driven by `scripts/notify.sh` in builder.

### Sub Repo
- **Preferred term:** `sub-repo`
- **Meaning:** One of the sibling product repos orchestrated by builder.

## Adapter Lifecycle / Visibility Terms

### Runtime Code Status
- **Preferred term:** `runtime code status`
- **Meaning:** The maturity/implementation state rendered in the adapter catalog (`seed`, `partial`, `stable`, `stale`, etc.).

### Distribution Level
- **Preferred term:** `distribution level`
- **Aliases / older wording:** `shipped level`, `repo only level`, `repo-only/debug-only/release visibility`
- **Meaning:** Where an adapter exists and is allowed to surface.
- **Current values include:**
  - `repo-only`
  - `debug-only`
  - `release`
  - `android release`
- **Why this term:** It covers repo-only/debug/release states better than the narrower word `shipped`.

### Visibility
- **Preferred term:** `visibility`
- **Meaning:** Whether a catalog entry is intended to appear in normal UI, debug-hidden UI, or report-only views.
- **Examples:** `normal`, `hidden`.

### Stable
- **Preferred term:** `stable`
- **Meaning:** Behavior is considered working enough for ordinary runtime use.

### Partial
- **Preferred term:** `partial`
- **Meaning:** Some runtime path exists, but it is incomplete, fragile, or missing major behavior.

### Stale
- **Preferred term:** `stale`
- **Meaning:** The implementation or metadata is no longer trusted to reflect the intended current state.

## Music / Sync Terms

### Song Metadata
- **Preferred term:** `song metadata`
- **Meaning:** Structured identity data for a song, such as title, artist, album, duration, source identity, and related detection fields.

### Canonical Duration
- **Preferred term:** `canonical duration`
- **Meaning:** The single trusted duration value the UI should use for progress and whole-song positioning.
- **Current likely sources:** SongSense metadata or LyricFlow-derived sung-part duration, depending on future policy.

### Offset
- **Preferred term:** `offset`
- **Meaning:** The time delta applied to align lyric focus or playback timing.

### Rate Coefficient
- **Preferred term:** `rate coefficient`
- **Aliases / older wording:** `rate`, `beat`, `coefficient`
- **Meaning:** The multiplicative timing correction value produced by SyncEngine-like logic.
- **Why this term:** It is more precise than `beat`, which is too musical/ambiguous for the actual scalar value.

### Sync Args
- **Preferred term:** `sync args`
- **Meaning:** The synchronization parameters passed into lyric shaping, typically offset plus rate-like correction.

### Lyric Unit
- **Preferred term:** `lyric unit`
- **Meaning:** The currently meaningful timed chunk for focus and rendering.
- **Examples:** word, line, paragraph-derived line focus.

### Granularity
- **Preferred term:** `granularity`
- **Meaning:** The lyric-unit resolution mode (`word`, `line`, `paragraph`) and related rendering policy.

### Granularity Zoom
- **Preferred term:** `granularity zoom`
- **Aliases / older wording:** `resolution`
- **Meaning:** The transient runtime step within the granularity ladder.
- **Why this term:** It separates the user's active zoom step from the permanent preference cap.

### Maximum Granularity
- **Preferred term:** `maximum granularity`
- **Meaning:** The finest lyric resolution the runtime may reach.

### Granularity Limit
- **Preferred term:** `granularity limit`
- **Meaning:** The settings-side cap on how far runtime may travel toward finer or coarser granularity states.

### Zoom
- **Preferred term:** `zoom`
- **Meaning:** The user input action that changes active granularity zoom, not browser-page zoom.

### Scroll
- **Preferred term:** `scroll`
- **Meaning:** Context-sensitive movement input.
- **Important distinction:** In lyric interactions, scroll may mean wheel-based granularity change or drag-based lyric-unit stepping depending on the active gesture and platform.

## UI / Interaction Terms

### Frozen Layer
- **Preferred term:** `frozen layer`
- **Meaning:** A sticky UI band that remains visible while the page beneath it scrolls.
- **Examples:** top report shell, `Current Section` banner, in-table sticky header.

### Filter
- **Preferred term:** `filter`
- **Meaning:** Column-level value/text/regex narrowing applied to a table.

### Reset Filter
- **Preferred term:** `reset filter`
- **Meaning:** Clear the currently applied filter for one column.

### Settings Storage
- **Preferred term:** `settings storage`
- **Meaning:** The persisted local preference state used by browser/runtime UI.

## Packaging / Release Terms

### Debug
- **Preferred term:** `debug`
- **Meaning:** A runtime/build profile that exposes additional instrumentation, hidden UI controls, or experimental visibility.

### Release
- **Preferred term:** `release`
- **Meaning:** A production-facing runtime/build profile intended for ordinary use.

### Repo-Only
- **Preferred term:** `repo-only`
- **Meaning:** Present only in repository metadata/inventory, not packaged for runtime use.

### Android Release
- **Preferred term:** `android release`
- **Meaning:** Released for Android runtime specifically, not necessarily cross-platform release-visible.

## Planning / Collaboration Terms

### Request
- **Preferred term:** `request`
- **Meaning:** A user instruction or desired work item in conversation.

### Task
- **Preferred term:** `task`
- **Meaning:** A scoped implementation step, usually tracked in `tasks.md` or repo-local task lists.

### Question
- **Preferred term:** `question`
- **Meaning:** A discussion item that should not automatically trigger implementation.

### Answer
- **Preferred term:** `answer`
- **Meaning:** The explicit response to a user question, distinct from implementation work.

### Progress
- **Preferred term:** `progress`
- **Meaning:** A milestone update indicating what has been completed, what remains, and what is in flight.

### Handoff
- **Preferred term:** `handoff`
- **Meaning:** A state-transfer artifact or summary intended to let the next human or agent continue work without reconstructing context from scratch.

## Cache / Contract Terms

### Contract
- **Preferred term:** `contract`
- **Meaning:** The structured schema/interface that system components agree on.

### Cache
- **Preferred term:** `cache`
- **Meaning:** Stored data or computed results reused to avoid redundant work.
- **Important project meaning:** often specifically used to prevent rate limiting or repeated external network requests.

### Test Inventory
- **Preferred term:** `test inventory`
- **Meaning:** The discovered total set of tests known to the system, regardless of whether a given run executes all of them.

## Naming Guidance Summary

Use these preferred terms in new writing when possible:
- `plugin bundle` instead of `plugin zip`
- `distribution level` instead of `shipped level`
- `rate coefficient` instead of bare `beat`
- `granularity zoom` instead of ambiguous `resolution`
- `feature seed` when introducing the concept formally

## Future Related Docs

This glossary is the first layer.

Likely next layers:
- `AGENTS.md` for repo-level coding-agent behavior and workflow routing
- repo-specific architecture docs for implementation details
- README links that route readers to the correct deeper docs instead of overloading this glossary
