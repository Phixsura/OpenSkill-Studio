"""Webhook Transformer — transform payloads between API formats using mapping rules.

Implements:
- Field mapping (rename, move, flatten, nest)
- Value transformation (type cast, format, template)
- Conditional mapping (only map if condition met)
- Default values for missing fields
- Multi-format support (flatten nested → flat, or vice versa)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import re


@dataclass
class FieldMapping:
    source: str       # source field path e.g. "user.name"
    target: str       # target field path e.g. "userName"
    transform: str = ""  # "uppercase", "lowercase", "int", "str", "bool", "template:..."
    default: object = None
    condition: str = ""  # "exists", "not_empty", "equals:value"


class WebhookTransformerService:
    def transform(self, payload: dict, mappings: list[FieldMapping]) -> dict:
        """Transform a payload according to mapping rules."""
        result = {}
        for mapping in mappings:
            value = self._get_nested(payload, mapping.source)

            # Check condition
            if mapping.condition:
                if not self._check_condition(value, mapping.condition):
                    continue

            # Apply default
            if value is None:
                value = mapping.default
                if value is None:
                    continue

            # Apply transform
            if mapping.transform:
                value = self._apply_transform(value, mapping.transform, payload)

            # Set in result
            self._set_nested(result, mapping.target, value)

        return result

    def _get_nested(self, obj: dict, path: str) -> object:
        """Get value from nested dict by dot-path."""
        parts = path.split(".")
        current = obj
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
            if current is None:
                return None
        return current

    def _set_nested(self, obj: dict, path: str, value: object) -> None:
        """Set value in nested dict by dot-path (creates intermediates)."""
        parts = path.split(".")
        current = obj
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value

    def _apply_transform(self, value: object, transform: str,
                         full_payload: dict) -> object:
        if transform == "uppercase":
            return str(value).upper()
        elif transform == "lowercase":
            return str(value).lower()
        elif transform == "int":
            try: return int(value)
            except (ValueError, TypeError): return 0
        elif transform == "str":
            return str(value)
        elif transform == "bool":
            return bool(value)
        elif transform.startswith("template:"):
            template = transform[9:]
            return self._render_template(template, full_payload)
        elif transform == "flatten_list":
            return ",".join(str(v) for v in value) if isinstance(value, list) else str(value)
        elif transform == "split":
            return str(value).split(",") if isinstance(value, str) else [value]
        return value

    def _render_template(self, template: str, payload: dict) -> str:
        """Simple template: "Hello {{name}}" → "Hello Alice"."""
        def replacer(m):
            path = m.group(1).strip()
            val = self._get_nested(payload, path)
            return str(val) if val is not None else ""
        return re.sub(r'\{\{(.+?)\}\}', replacer, template)

    def _check_condition(self, value: object, condition: str) -> bool:
        if condition == "exists":
            return value is not None
        if condition == "not_empty":
            return value is not None and value != "" and value != [] and value != {}
        if condition.startswith("equals:"):
            expected = condition[7:]
            return str(value) == expected
        return True

    def flatten(self, payload: dict, prefix: str = "") -> dict:
        """Flatten nested dict: {"a": {"b": 1}} → {"a.b": 1}."""
        result = {}
        for key, value in payload.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                result.update(self.flatten(value, full_key))
            else:
                result[full_key] = value
        return result

    def unflatten(self, flat: dict) -> dict:
        """Unflatten: {"a.b": 1} → {"a": {"b": 1}}."""
        result = {}
        for key, value in flat.items():
            self._set_nested(result, key, value)
        return result
