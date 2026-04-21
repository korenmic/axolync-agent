---
name: addon-native-runtime-operator
description: Implement a new addon-owned native bridge runtime operator across addon, builder, browser, and wrapper hosts. Use when an addon needs a background native helper, localhost server, or host-managed native process similar to Vibra native proxy.
---

# Addon Native Runtime Operator

## Overview

Use this skill when an addon needs a native bridge runtime operator that runs outside plain browser JS and is surfaced through the shared Axolync native bridge.

This skill is a guided entry point. The full source of truth lives in the builder playbook:

- `axolync-builder/docs/native-bridge-runtime-operator-playbook.md`

Read that file first. It contains the architecture, ownership rules, wrapper-specific steps, failure modes, and the handoff prompt.

## Use This Skill When

- a new addon needs a native background helper
- an addon needs a localhost server surfaced through the host
- you need to reproduce the Vibra native proxy architecture for another addon
- you need to add wrapper support for Electron, Tauri, or Capacitor Android without breaking the others

## Workflow

1. Read the builder playbook first.
2. Identify the ownership split:
   - addon repo
   - builder
   - browser
   - wrapper host repo
3. Reuse the normalized terms:
   - native bridge
   - runtime operator
   - native bridge operation
4. Keep addon JS generic:
   - start through the generic bridge
   - call `getConnection()`
   - use the returned connection
5. Keep wrapper-specific fixes narrow:
   - Capacitor quirks stay in Android/Capacitor
   - do not regress Tauri/Electron
6. Add proof at the hardest host boundary, not just packaging proof.

## Deliverables

A complete implementation should usually include:

- addon manifest declarations
- addon package native payload metadata
- builder staging and artifact proof
- browser generic bridge consumption
- wrapper host bridge publication and lifecycle support
- tests proving the operator is callable and its connection is usable

## Reference Material

- Playbook:
  - `axolync-builder/docs/native-bridge-runtime-operator-playbook.md`
- Ready-to-forward handoff prompt:
  - `skills/addon-native-runtime-operator/references/handoff-prompt.md`

## Final Rule

Do not re-invent the bridge surface per addon. Reuse the shared architecture and treat the Vibra implementation as the reference pattern.
