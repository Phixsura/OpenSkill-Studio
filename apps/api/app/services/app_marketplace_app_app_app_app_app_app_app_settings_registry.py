"""Platform settings registry — centralized settings with validation and defaults."""
from __future__ import annotations
import copy


SCHEMA = {
    "general": {
        "platform_name": {"type": "string", "default": "OpenSkill", "required": True},
        "support_email": {"type": "string", "default": "support@openskill.io"},
        "maintenance_mode": {"type": "boolean", "default": False},
    },
    "security": {
        "mfa_required": {"type": "boolean", "default": False},
        "session_timeout_min": {"type": "integer", "default": 60, "min": 5, "max": 1440},
        "password_min_length": {"type": "integer", "default": 8, "min": 8, "max": 128},
    },
    "notifications": {
        "email_enabled": {"type": "boolean", "default": True},
        "slack_enabled": {"type": "boolean", "default": False},
        "digest_frequency": {"type": "string", "default": "daily", "enum": ["daily", "weekly", "never"]},
    },
}


def get_defaults() -> dict:
    return {section: {k: v["default"] for k, v in fields.items()}
            for section, fields in SCHEMA.items()}


def validate_settings(settings: dict) -> dict:
    errors = []
    for section, fields in SCHEMA.items():
        section_vals = settings.get(section, {})
        for key, schema in fields.items():
            val = section_vals.get(key)
            if val is None:
                continue
            if schema["type"] == "integer" and isinstance(val, int):
                if "min" in schema and val < schema["min"]:
                    errors.append(f"{section}.{key}: must be >= {schema['min']}")
                if "max" in schema and val > schema["max"]:
                    errors.append(f"{section}.{key}: must be <= {schema['max']}")
            if "enum" in schema and val not in schema["enum"]:
                errors.append(f"{section}.{key}: must be one of {schema['enum']}")
    return {"valid": len(errors) == 0, "errors": errors}


def merge_settings(defaults: dict, overrides: dict) -> dict:
    result = copy.deepcopy(defaults)
    for section, fields in overrides.items():
        if section in result and isinstance(fields, dict):
            result[section].update(fields)
    return result
