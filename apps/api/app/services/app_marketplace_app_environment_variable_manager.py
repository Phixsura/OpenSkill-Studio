"""Environment variable manager — secure env var storage with masking."""

import re

SENSITIVE_PATTERNS = {"password", "secret", "token", "key", "api_key", "private"}


def is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(p in lower for p in SENSITIVE_PATTERNS)


def mask_value(value: str) -> str:
    if len(value) <= 4:
        return "****"
    return value[:2] + "*" * (len(value) - 4) + value[-2:]


def set_env_var(*, app_id: str, key: str, value: str, environment: str = "production") -> dict:
    if not re.match(r'^[A-Z][A-Z0-9_]*$', key):
        return {"error": "Key must be uppercase with underscores (e.g., MY_VAR)"}
    return {"app_id": app_id, "key": key,
            "display_value": mask_value(value) if is_sensitive(key) else value,
            "environment": environment, "sensitive": is_sensitive(key), "error": None}


def list_env_vars(*, vars: list[dict]) -> list[dict]:
    return [{"key": v["key"], "value": mask_value(v["value"]) if is_sensitive(v["key"]) else v["value"],
             "sensitive": is_sensitive(v["key"]), "environment": v.get("environment", "production")}
            for v in vars]
