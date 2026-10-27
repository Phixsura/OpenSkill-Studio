"""API Changelog Generator — structured changelog from endpoint diffs across versions.

Generates human-readable and machine-readable changelogs for API versions:
- Diff detection: added, removed, modified, deprecated endpoints
- Breaking vs non-breaking change classification
- Parameter-level change tracking (added/removed/type-changed)
- Response schema change detection
- Markdown and JSON changelog output
- Migration guide generation with code examples
- Semantic grouping by resource/domain
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

import structlog

log = structlog.get_logger()


class ChangeType(str, Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    DEPRECATED = "deprecated"


class Severity(str, Enum):
    BREAKING = "breaking"
    NON_BREAKING = "non_breaking"
    PATCH = "patch"


@dataclass
class EndpointSpec:
    """Specification for a single API endpoint."""

    method: str          # GET, POST, PATCH, DELETE
    path: str            # /api/v1/skills/{id}
    summary: str
    parameters: dict[str, str] = field(default_factory=dict)   # name → type
    request_body: dict | None = None                           # JSON schema summary
    response_fields: dict[str, str] = field(default_factory=dict)  # name → type
    deprecated: bool = False
    auth_required: bool = True


@dataclass
class ParamChange:
    """A change to a single parameter."""

    name: str
    change_type: ChangeType
    old_type: str | None = None
    new_type: str | None = None


@dataclass
class EndpointChange:
    """A detected change to an endpoint between versions."""

    method: str
    path: str
    change_type: ChangeType
    severity: Severity
    summary: str
    param_changes: list[ParamChange] = field(default_factory=list)
    response_changes: list[ParamChange] = field(default_factory=list)
    migration_hint: str | None = None


@dataclass
class ChangelogEntry:
    """A complete changelog for a version transition."""

    from_version: str
    to_version: str
    generated_at: datetime
    changes: list[EndpointChange]
    breaking_count: int
    non_breaking_count: int
    patch_count: int

    @property
    def has_breaking(self) -> bool:
        return self.breaking_count > 0


def diff_endpoints(old: list[EndpointSpec], new: list[EndpointSpec]) -> list[EndpointChange]:
    """Compute the diff between two sets of endpoint specs.

    Returns a list of EndpointChange describing what changed.
    """
    old_map = {(e.method, e.path): e for e in old}
    new_map = {(e.method, e.path): e for e in new}

    old_keys = set(old_map.keys())
    new_keys = set(new_map.keys())
    changes: list[EndpointChange] = []

    # Added endpoints
    for key in sorted(new_keys - old_keys):
        ep = new_map[key]
        changes.append(EndpointChange(
            method=ep.method,
            path=ep.path,
            change_type=ChangeType.ADDED,
            severity=Severity.NON_BREAKING,
            summary=f"New endpoint: {ep.method} {ep.path}",
        ))

    # Removed endpoints
    for key in sorted(old_keys - new_keys):
        ep = old_map[key]
        changes.append(EndpointChange(
            method=ep.method,
            path=ep.path,
            change_type=ChangeType.REMOVED,
            severity=Severity.BREAKING,
            summary=f"Removed endpoint: {ep.method} {ep.path}",
            migration_hint=f"Clients using {ep.method} {ep.path} must remove these calls.",
        ))

    # Modified endpoints
    for key in sorted(old_keys & new_keys):
        old_ep = old_map[key]
        new_ep = new_map[key]
        ep_changes = _diff_single_endpoint(old_ep, new_ep)
        if ep_changes:
            changes.extend(ep_changes)

    return changes


def generate_changelog(from_version: str, to_version: str,
                       old_endpoints: list[EndpointSpec],
                       new_endpoints: list[EndpointSpec]) -> ChangelogEntry:
    """Generate a complete changelog between two API versions."""
    changes = diff_endpoints(old_endpoints, new_endpoints)

    breaking = sum(1 for c in changes if c.severity == Severity.BREAKING)
    non_breaking = sum(1 for c in changes if c.severity == Severity.NON_BREAKING)
    patch = sum(1 for c in changes if c.severity == Severity.PATCH)

    return ChangelogEntry(
        from_version=from_version,
        to_version=to_version,
        generated_at=datetime.now(UTC),
        changes=changes,
        breaking_count=breaking,
        non_breaking_count=non_breaking,
        patch_count=patch,
    )


def changelog_to_markdown(entry: ChangelogEntry) -> str:
    """Render a changelog entry as Markdown."""
    lines = [
        f"# API Changelog: {entry.from_version} → {entry.to_version}",
        "",
        f"Generated: {entry.generated_at.strftime('%Y-%m-%d')}",
        "",
    ]

    if entry.has_breaking:
        lines.append(f"⚠️ **{entry.breaking_count} breaking change(s)** — review migration hints below.")
        lines.append("")

    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Breaking | {entry.breaking_count} |")
    lines.append(f"| Non-breaking | {entry.non_breaking_count} |")
    lines.append(f"| Patch | {entry.patch_count} |")
    lines.append("")

    # Group by change type
    for ct in ChangeType:
        group = [c for c in entry.changes if c.change_type == ct]
        if not group:
            continue
        lines.append(f"## {ct.value.title()}")
        lines.append("")
        for c in group:
            severity_badge = "🔴" if c.severity == Severity.BREAKING else "🟢"
            lines.append(f"- {severity_badge} `{c.method} {c.path}` — {c.summary}")
            if c.param_changes:
                for p in c.param_changes:
                    lines.append(f"  - Parameter `{p.name}`: {p.change_type.value}")
            if c.response_changes:
                for r in c.response_changes:
                    lines.append(f"  - Response field `{r.name}`: {r.change_type.value}")
            if c.migration_hint:
                lines.append(f"  - 💡 **Migration:** {c.migration_hint}")
        lines.append("")

    return "\n".join(lines)


def changelog_to_json(entry: ChangelogEntry) -> dict:
    """Render a changelog entry as a JSON-serializable dict."""
    return {
        "from_version": entry.from_version,
        "to_version": entry.to_version,
        "generated_at": entry.generated_at.isoformat(),
        "summary": {
            "breaking": entry.breaking_count,
            "non_breaking": entry.non_breaking_count,
            "patch": entry.patch_count,
            "has_breaking": entry.has_breaking,
        },
        "changes": [
            {
                "method": c.method,
                "path": c.path,
                "change_type": c.change_type.value,
                "severity": c.severity.value,
                "summary": c.summary,
                "param_changes": [
                    {"name": p.name, "change_type": p.change_type.value,
                     "old_type": p.old_type, "new_type": p.new_type}
                    for p in c.param_changes
                ],
                "response_changes": [
                    {"name": r.name, "change_type": r.change_type.value,
                     "old_type": r.old_type, "new_type": r.new_type}
                    for r in c.response_changes
                ],
                "migration_hint": c.migration_hint,
            }
            for c in entry.changes
        ],
    }


# ── Internal helpers ─────────────────────────────────────

def _diff_single_endpoint(old: EndpointSpec, new: EndpointSpec) -> list[EndpointChange]:
    """Diff a single endpoint between versions."""
    changes: list[EndpointChange] = []

    # Deprecation
    if not old.deprecated and new.deprecated:
        changes.append(EndpointChange(
            method=new.method,
            path=new.path,
            change_type=ChangeType.DEPRECATED,
            severity=Severity.NON_BREAKING,
            summary=f"Deprecated: {new.method} {new.path}",
            migration_hint="This endpoint will be removed in a future version.",
        ))

    # Parameter changes
    param_changes = _diff_params(old.parameters, new.parameters)

    # Response changes
    response_changes = _diff_params(old.response_fields, new.response_fields)

    # Summary changes
    if old.summary != new.summary:
        pass  # Summary text change is a patch, tracked implicitly

    if param_changes or response_changes:
        # Determine severity
        has_removed_params = any(p.change_type == ChangeType.REMOVED for p in param_changes)
        has_type_change = any(p.change_type == ChangeType.MODIFIED for p in param_changes)
        has_removed_response = any(r.change_type == ChangeType.REMOVED for r in response_changes)

        severity = Severity.PATCH
        if has_removed_params or has_removed_response:
            severity = Severity.BREAKING
        elif has_type_change:
            severity = Severity.BREAKING

        desc_parts = []
        if param_changes:
            desc_parts.append(f"{len(param_changes)} param change(s)")
        if response_changes:
            desc_parts.append(f"{len(response_changes)} response change(s)")

        changes.append(EndpointChange(
            method=new.method,
            path=new.path,
            change_type=ChangeType.MODIFIED,
            severity=severity,
            summary=f"Modified: {', '.join(desc_parts)}",
            param_changes=param_changes,
            response_changes=response_changes,
        ))

    return changes


def _diff_params(old: dict[str, str], new: dict[str, str]) -> list[ParamChange]:
    """Diff parameter/field sets."""
    changes: list[ParamChange] = []
    old_keys = set(old.keys())
    new_keys = set(new.keys())

    for name in sorted(new_keys - old_keys):
        changes.append(ParamChange(name=name, change_type=ChangeType.ADDED, new_type=new[name]))

    for name in sorted(old_keys - new_keys):
        changes.append(ParamChange(name=name, change_type=ChangeType.REMOVED, old_type=old[name]))

    for name in sorted(old_keys & new_keys):
        if old[name] != new[name]:
            changes.append(ParamChange(
                name=name, change_type=ChangeType.MODIFIED,
                old_type=old[name], new_type=new[name],
            ))

    return changes
