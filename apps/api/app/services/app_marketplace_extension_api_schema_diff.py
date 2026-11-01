"""API Schema Diff — deep structural comparison of API schemas.

Detects:
- Added/removed/modified fields at any nesting depth
- Type changes (string→int, etc.)
- Required field changes
- Enum value changes
- Breaking vs non-breaking classification
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class ChangeKind(str, Enum):
    ADDED = "added"
    REMOVED = "removed"
    TYPE_CHANGED = "type_changed"
    REQUIRED_ADDED = "required_added"
    REQUIRED_REMOVED = "required_removed"
    ENUM_ADDED = "enum_values_added"
    ENUM_REMOVED = "enum_values_removed"
    DEFAULT_CHANGED = "default_changed"
    DESCRIPTION_CHANGED = "description_changed"


BREAKING_CHANGES = {
    ChangeKind.REMOVED, ChangeKind.TYPE_CHANGED,
    ChangeKind.REQUIRED_ADDED, ChangeKind.ENUM_REMOVED,
}


@dataclass
class SchemaDiff:
    path: str  # e.g. "User.email", "Order.items[].price"
    kind: ChangeKind
    old_value: str = ""
    new_value: str = ""
    breaking: bool = False

    def __post_init__(self):
        self.breaking = self.kind in BREAKING_CHANGES


class ApiSchemaDiffService:
    def diff_schemas(self, old: dict, new: dict, path: str = "") -> list[SchemaDiff]:
        """Recursively diff two schema objects (simplified JSON Schema)."""
        diffs: list[SchemaDiff] = []
        old_fields = old.get("properties", {})
        new_fields = new.get("properties", {})
        old_required = set(old.get("required", []))
        new_required = set(new.get("required", []))

        all_keys = set(old_fields) | set(new_fields)

        for key in sorted(all_keys):
            field_path = f"{path}.{key}" if path else key

            if key not in old_fields:
                diffs.append(SchemaDiff(field_path, ChangeKind.ADDED,
                                       new_value=str(new_fields[key].get("type", "unknown"))))
                continue

            if key not in new_fields:
                diffs.append(SchemaDiff(field_path, ChangeKind.REMOVED,
                                       old_value=str(old_fields[key].get("type", "unknown"))))
                continue

            old_f = old_fields[key]
            new_f = new_fields[key]

            # Type change
            if old_f.get("type") != new_f.get("type"):
                diffs.append(SchemaDiff(field_path, ChangeKind.TYPE_CHANGED,
                                       old_value=str(old_f.get("type")),
                                       new_value=str(new_f.get("type"))))

            # Enum changes
            old_enum = set(old_f.get("enum", []))
            new_enum = set(new_f.get("enum", []))
            if old_enum and new_enum:
                removed_vals = old_enum - new_enum
                added_vals = new_enum - old_enum
                if removed_vals:
                    diffs.append(SchemaDiff(field_path, ChangeKind.ENUM_REMOVED,
                                           old_value=str(removed_vals)))
                if added_vals:
                    diffs.append(SchemaDiff(field_path, ChangeKind.ENUM_ADDED,
                                           new_value=str(added_vals)))

            # Default change
            if old_f.get("default") != new_f.get("default") and \
               ("default" in old_f or "default" in new_f):
                diffs.append(SchemaDiff(field_path, ChangeKind.DEFAULT_CHANGED,
                                       old_value=str(old_f.get("default", "")),
                                       new_value=str(new_f.get("default", ""))))

            # Recurse into nested objects
            if old_f.get("type") == "object" and new_f.get("type") == "object":
                diffs.extend(self.diff_schemas(old_f, new_f, field_path))

            # Array items
            if old_f.get("type") == "array" and new_f.get("type") == "array":
                old_items = old_f.get("items", {})
                new_items = new_f.get("items", {})
                if old_items.get("type") != new_items.get("type"):
                    diffs.append(SchemaDiff(f"{field_path}[]", ChangeKind.TYPE_CHANGED,
                                           old_value=str(old_items.get("type")),
                                           new_value=str(new_items.get("type"))))
                if old_items.get("properties"):
                    diffs.extend(self.diff_schemas(old_items, new_items, f"{field_path}[]"))

        # Required field changes
        for key in new_required - old_required:
            if key in old_fields:  # only breaking if field existed
                fp = f"{path}.{key}" if path else key
                diffs.append(SchemaDiff(fp, ChangeKind.REQUIRED_ADDED))

        for key in old_required - new_required:
            fp = f"{path}.{key}" if path else key
            diffs.append(SchemaDiff(fp, ChangeKind.REQUIRED_REMOVED))

        return diffs

    def summarize(self, diffs: list[SchemaDiff]) -> dict:
        breaking = [d for d in diffs if d.breaking]
        non_breaking = [d for d in diffs if not d.breaking]
        by_kind = {}
        for d in diffs:
            by_kind[d.kind.value] = by_kind.get(d.kind.value, 0) + 1
        return {
            "total_changes": len(diffs),
            "breaking_count": len(breaking),
            "non_breaking_count": len(non_breaking),
            "by_kind": by_kind,
            "is_backward_compatible": len(breaking) == 0,
            "breaking_paths": [d.path for d in breaking],
        }
