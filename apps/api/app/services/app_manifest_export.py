"""Manifest export — export manifest in different formats."""

import json
import copy


def export_as_json(manifest: dict, *, pretty: bool = True) -> str:
    return json.dumps(manifest, indent=2 if pretty else None, sort_keys=True)


def export_as_yaml_like(manifest: dict) -> str:
    """Simple YAML-like export (no PyYAML dependency)."""
    lines = []
    _render(manifest, lines, indent=0)
    return "\n".join(lines)


def _render(obj, lines, indent):
    prefix = "  " * indent
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{prefix}{k}:")
                _render(v, lines, indent + 1)
            else:
                lines.append(f"{prefix}{k}: {json.dumps(v)}")
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}-")
                _render(item, lines, indent + 1)
            else:
                lines.append(f"{prefix}- {json.dumps(item)}")


def strip_internal_fields(manifest: dict) -> dict:
    """Remove internal-only fields before export."""
    m = copy.deepcopy(manifest)
    for field in ["_id", "_internal", "_created_by", "_review_notes"]:
        m.pop(field, None)
    return m
