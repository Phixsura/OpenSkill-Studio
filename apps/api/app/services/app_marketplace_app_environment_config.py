"""App environment config — manage env vars and secrets for apps."""

import re
import secrets


ENV_KEY_RE = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")


def validate_env_key(*, key: str) -> dict:
    if not ENV_KEY_RE.match(key):
        return {"valid": False, "error": "Key must be uppercase alphanumeric with underscores, starting with a letter"}
    return {"valid": True, "key": key}


def set_env_var(*, app_id: str, key: str, value: str, is_secret: bool = False) -> dict:
    v = validate_env_key(key=key)
    if not v["valid"]:
        return {"success": False, "error": v["error"]}
    masked = "••••••••" if is_secret else value
    return {"success": True, "app_id": app_id, "key": key,
            "display_value": masked, "is_secret": is_secret,
            "encryption_key_id": f"kms_{secrets.token_hex(4)}" if is_secret else None}


def list_env_vars(*, app_id: str) -> dict:
    return {
        "app_id": app_id,
        "variables": [
            {"key": "DATABASE_URL", "display_value": "••••••••", "is_secret": True},
            {"key": "API_BASE_URL", "display_value": "https://api.example.com", "is_secret": False},
            {"key": "LOG_LEVEL", "display_value": "info", "is_secret": False},
        ],
        "total": 3,
        "secret_count": 1,
    }
