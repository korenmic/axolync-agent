# Axolync Repo Summaries

This file is a short self-contained orientation summary for the active Axolync repos.

## axolync-builder

Role:

- workspace bootstrap authority
- reporting and inspect authority
- cross-repo orchestration
- build, package, mirror, and artifact generation

Read first when you need:

- repo topology
- seed/spec workflow norms
- report generation
- builder presets and publication logic

Primary docs in this mirror:

- [axolync-builder.bootstrap.md](./axolync-builder.bootstrap.md)
- [axolync-builder.bootstrap-prompt.md](./axolync-builder.bootstrap-prompt.md)
- [axolync.vocabulary.md](./axolync.vocabulary.md)

## axolync-browser

Role:

- main product runtime
- state machine
- Stage 1 addon host
- live listening, SongSense, SyncEngine, LyricFlow orchestration
- user-facing settings and debug surfaces

Read first when you need:

- product behavior
- state transitions
- playback gating
- live query flow

Important bootstrap-adjacent doc mirrored here:

- [axolync-browser.local-dependency-bootstrap-policy.md](./axolync-browser.local-dependency-bootstrap-policy.md)

## axolync-addon-whisper

Role:

- Whisper-owned addon runtime
- model catalog and model-management truth
- SongSense and SyncEngine speech paths inside the addon
- worker/runtime/inference authority for the Whisper addon

Read first when you need:

- Whisper runtime behavior
- model-management truth
- addon-owned debug and inference logic

Important bootstrap-adjacent doc mirrored here:

- [axolync-addon-whisper.local-dependency-bootstrap-policy.md](./axolync-addon-whisper.local-dependency-bootstrap-policy.md)

## axolync-plugins-contract

Role:

- shared addon/adapter/query contract authority
- package metadata and runtime data surface definitions
- compatibility boundary between browser and addons

Read first when you need:

- contract questions
- package schema questions
- query compatibility questions

## axolync-agent

Role:

- self-contained agent-support repo for Axolync
- local copies of Axolync-specific skills
- bootstrap and queue/task-id conventions

Use it for:

- reviewing local skill logic
- sharing task ids across workspaces
- keeping bootstrap/agent docs in one place

Maintenance rule:

- if any repo's core role, authority boundaries, bootstrap workflow, or critical vocabulary changes, the mirrored summaries in this repo must be updated too
