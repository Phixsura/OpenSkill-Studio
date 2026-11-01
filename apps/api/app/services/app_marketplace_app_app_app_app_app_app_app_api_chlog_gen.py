"""API changelog generator — auto-generate changelogs from OpenAPI diffs."""
from __future__ import annotations


def diff_openapi(old_spec: dict, new_spec: dict) -> dict:
    old_paths = set(old_spec.get("paths", {}).keys())
    new_paths = set(new_spec.get("paths", {}).keys())
    added = sorted(new_paths - old_paths)
    removed = sorted(old_paths - new_paths)
    modified = []
    for path in sorted(old_paths & new_paths):
        old_methods = set(old_spec["paths"][path].keys())
        new_methods = set(new_spec["paths"][path].keys())
        if old_methods != new_methods:
            modified.append({"path": path,
                              "added_methods": sorted(new_methods - old_methods),
                              "removed_methods": sorted(old_methods - new_methods)})
    breaking = len(removed) > 0 or any(m.get("removed_methods") for m in modified)
    return {"added_paths": added, "removed_paths": removed,
            "modified_paths": modified, "breaking": breaking,
            "total_changes": len(added) + len(removed) + len(modified)}


def format_changelog(diff: dict, version: str) -> str:
    lines = [f"## {version}"]
    if diff["added_paths"]:
        lines.append("\n### Added")
        for p in diff["added_paths"]:
            lines.append(f"- `{p}`")
    if diff["removed_paths"]:
        lines.append("\n### Removed ⚠️ BREAKING")
        for p in diff["removed_paths"]:
            lines.append(f"- `{p}`")
    if diff["modified_paths"]:
        lines.append("\n### Modified")
        for m in diff["modified_paths"]:
            lines.append(f"- `{m['path']}`")
    return "\n".join(lines)
