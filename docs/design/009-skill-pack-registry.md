# ADR-009: Skill Pack Registry & Versioned Content Distribution

## Status: Accepted

## Context

OpenSkill Studio needs a content distribution layer that allows curriculum designers to package, version, and share training content across organizations. Currently, skills, exercises, categories, and project templates are created manually within each organization. There is no mechanism to distribute pre-built curricula, track upstream changes, or safely import third-party content.

A registry system must support:

- Packaging multiple related components (categories, skills, exercises, project templates) into a single distributable unit
- Semantic versioning with immutable release snapshots
- Safe installation into target organizations with full data isolation
- Forking to permanently sever upstream tracking
- Public, unlisted, and private visibility controls
- Security validation of imported content

## Decision

### Data Model

Three new tables support the registry:

- **SkillPack** -- represents a publishable pack with metadata (name, slug, description, difficulty, tags, provenance, visibility). Owned by an organization.
- **SkillPackRelease** -- an immutable versioned snapshot containing a JSON manifest of all components. Each release is append-only; published releases cannot be modified.
- **SkillPackInstallation** -- tracks which release was installed into which organization, along with the installation timestamp and status.

The manifest uses **logical_ids** (slug-based, e.g. `"cat:frontend-basics"`, `"skill:react-hooks"`) instead of database ULIDs. This ensures packs are portable across environments without foreign-key collisions.

### Manifest Schema

Each release manifest follows this structure:

```json
{
  "schema_version": "1",
  "pack": {
    "slug": "frontend-fundamentals",
    "name": "Frontend Fundamentals",
    "difficulty": "beginner"
  },
  "categories": [
    {
      "logical_id": "cat:html-basics",
      "name": "HTML Basics",
      "sort_order": 1
    }
  ],
  "skills": [
    {
      "logical_id": "skill:semantic-html",
      "category_ref": "cat:html-basics",
      "name": "Semantic HTML",
      "difficulty": "beginner",
      "exercises": [
        {
          "logical_id": "ex:build-nav",
          "title": "Build a Navigation Bar",
          "type": "practice",
          "prerequisites": ["ex:intro-tags"]
        }
      ]
    }
  ],
  "project_templates": [
    {
      "logical_id": "tpl:portfolio-site",
      "name": "Portfolio Website",
      "skill_refs": ["skill:semantic-html"]
    }
  ]
}
```

- Prerequisites reference logical_ids within the manifest, not database IDs.
- All references are validated at publish time.

### Installation

Installation creates **independent copies** with new ULIDs in the target organization:

1. Parse the manifest from the selected release
2. Create new database records for each component (categories, skills, exercises, project templates) with fresh ULIDs
3. Remap all internal references (category FK, prerequisite links) to the newly generated IDs
4. Set origin tracking columns on each created record:
   - `origin_pack_id` -- the source SkillPack ID
   - `origin_release_id` -- the source SkillPackRelease ID
   - `origin_component_id` -- the logical_id from the manifest
   - `locally_modified` -- boolean flag, initially `false`

The `locally_modified` flag is set to `true` whenever a user edits an installed component. This enables conflict detection when checking for upstream updates.

### Fork

Forking **permanently severs the upstream link**:

- All origin tracking columns (`origin_pack_id`, `origin_release_id`, `origin_component_id`) are set to `NULL`
- The `locally_modified` flag is cleared
- The SkillPackInstallation record is marked as `forked`
- There is no un-fork operation

### Import Security

Manifest import applies 11 validation steps in order:

1. **Size check** -- reject uploads exceeding 50 MB
2. **Zip validity** -- verify the archive is a valid ZIP file
3. **File count** -- reject archives with more than 500 entries
4. **Path traversal** -- reject any entry with `..` or absolute paths
5. **Decompression bomb** -- reject if decompressed size exceeds 200 MB
6. **Manifest presence** -- require `manifest.json` at the archive root
7. **Manifest parsing** -- validate JSON syntax
8. **Schema version** -- reject unsupported `schema_version` values
9. **Structure validation** -- validate all required fields and types
10. **Logical ID uniqueness** -- reject duplicate logical_ids within the manifest
11. **Prerequisite references** -- verify all prerequisite refs point to existing logical_ids

**Install-time invariants validated at import (R86).** Some manifest fields are
not consumed by the import writer itself but by the *install* writer that
materializes the manifest into org content later. A malformed value passes
import, reaches PUBLISHED, and then crashes **every** install — an
unrecoverable published-but-uninstallable pack. Import therefore also enforces:

- **Non-finite floats** -- `json.loads` accepts the bare tokens
  `NaN`/`Infinity`/`-Infinity` and yields real `float('nan')`/`float('inf')`;
  the default JSONB serializer re-emits them verbatim and Postgres rejects them
  (22P02) at the manifest insert. The NUL-scan walk over the parsed manifest
  also rejects non-finite floats (parity with every other JSONB write surface).
- **Category references** -- a skill's `category_logical_id` is resolved against
  the manifest `categories[]` at install (`CATEGORY_NOT_FOUND`). Import
  type-gates `categories[]` and rejects any skill referencing a category the
  manifest never defined, so the dangling reference is caught at import time.
- **Integer-column fields** -- exercise `max_score` / `sort_order` and skill
  `sort_order` flow verbatim into INTEGER columns at install with only a
  `.get(default)`. Import type-gates them (bool excluded, an int subclass) and
  bounds `max_score` to 1–10000.

Runtime-only fields (database IDs, timestamps, internal FKs) are stripped from the manifest before processing.

### Registry Visibility

Packs support three visibility levels:

- **PRIVATE** -- only the owning organization can view and install
- **UNLISTED** -- accessible via direct link but not discoverable in search results
- **PUBLIC** -- fully discoverable in the registry search

Visibility is set at the pack level and applies to all releases.

## Consequences

### Positive

- Packs are fully portable across environments because they use logical_ids rather than FK references
- Organizations retain full ownership of installed content -- no runtime dependency on the source
- Origin tracking enables upgrade-awareness without forcing automatic updates
- The 11-step import validation provides defense-in-depth against malicious archives
- Semantic versioning with immutable releases provides a clear content history

### Negative

- Upgrades require explicit user action (no auto-update mechanism)
- Fork is permanent and cannot be undone
- Logical ID scheme adds complexity to the manifest authoring process
- Each installation creates full copies of all components, increasing storage usage proportionally
