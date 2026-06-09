# Agent Descriptor-Owned Test Command Exports Design

## Overview

Make Agent command metadata descriptor-owned and align the repo itself with the add-consumed-repo descriptor standard.

## Design

- Add descriptor exports for Agent build, sanity, and full-test commands.
- Preserve existing skill and dispatch behavior.
- Validate Builder report discovery through descriptor exports.

## Non-Goals

- No skill behavior changes except descriptor guidance already covered by the separate skill-standard spec.
- No workspace boundary relaxation.
