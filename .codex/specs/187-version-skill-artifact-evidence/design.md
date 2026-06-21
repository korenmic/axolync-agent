# Design

## Overview

Extend `workspace_version_ops.py` with evidence collection helpers that inspect common addon package ZIP outputs and browser preinstalled metadata. Keep `versionFile` as authority and add evidence fields to emitted rows.

## Output

Rows gain:

- `artifactEvidenceStatus`
- `artifactEvidenceVersions`
- `artifactEvidenceDetails`

Text/Markdown tables include a compact evidence status column.

## Validation

Update or add tests around inventory/verify behavior using fixture repos.
