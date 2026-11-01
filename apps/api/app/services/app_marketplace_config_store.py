"""Config Store — typed configuration management for extensions.

Each extension can store and retrieve configuration per-org,
with schema validation, defaults, and secret masking.
"""
from __future__ import annotations
from copy import deepcopy


class ConfigStore:
    """Per-org, per-extension configuration store with schema validation."""

    def __init__(self):
        self._configs: dict[str, dict[str, dict]] = {}  # org -> ext -> config
        self._schemas: dict[str, dict] = {}  # ext -> schema
        self._defaults: dict[str, dict] = {}  # ext -> defaults

    def register_schema(self, extension_id: str, schema: dict, defaults: dict | None = None) -> None:
        """Register config schema for an extension."""
        self._schemas[extension_id] = schema
        self._defaults[extension_id] = defaults or {}

    def validate(self, extension_id: str, config: dict) -> tuple[bool, list[str]]:
        """Validate config against registered schema."""
        schema = self._schemas.get(extension_id, {})
        errors = []
        for field_name, field_def in schema.items():
            required = field_def.get("required", False)
            field_type = field_def.get("type", "string")
            if required and field_name not in config:
                errors.append(f"Missing required field: {field_name}")
            elif field_name in config:
                value = config[field_name]
                type_map = {"string": str, "int": int, "bool": bool, "float": float, "list": list}
                expected = type_map.get(field_type)
                if expected and not isinstance(value, expected):
                    errors.append(f"Field {field_name}: expected {field_type}, got {type(value).__name__}")
        return len(errors) == 0, errors

    def set_config(self, org_id: str, extension_id: str, config: dict) -> tuple[bool, list[str]]:
        """Set configuration, merging with defaults and validating."""
        merged = {**self._defaults.get(extension_id, {}), **config}
        valid, errors = self.validate(extension_id, merged)
        if not valid:
            return False, errors
        if org_id not in self._configs:
            self._configs[org_id] = {}
        self._configs[org_id][extension_id] = merged
        return True, []

    def get_config(self, org_id: str, extension_id: str, mask_secrets: bool = False) -> dict:
        """Get config, optionally masking secret fields."""
        config = self._configs.get(org_id, {}).get(extension_id, {})
        if not mask_secrets or not config:
            return deepcopy(config)
        schema = self._schemas.get(extension_id, {})
        masked = deepcopy(config)
        for field_name, field_def in schema.items():
            if field_def.get("secret") and field_name in masked:
                masked[field_name] = "***"
        return masked

    def delete_config(self, org_id: str, extension_id: str) -> bool:
        """Delete configuration for an extension in an org."""
        if org_id in self._configs and extension_id in self._configs[org_id]:
            del self._configs[org_id][extension_id]
            return True
        return False

    def list_configured(self, org_id: str) -> list[str]:
        """List extension IDs that have config set for an org."""
        return list(self._configs.get(org_id, {}).keys())
