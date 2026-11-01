"""Environment variable manager — manage app env vars with masking."""
from __future__ import annotations
import re

SENSITIVE_PATTERNS = re.compile(r"(key|secret|token|password|pwd|auth|credential)", re.IGNORECASE)


def set_env_var(store: dict, key: str, value: str, is_secret: bool = False) -> dict:
    if not re.match(r"^[A-Z_][A-Z0-9_]*$", key):
        return {"set": False, "error": "invalid_key_format"}
    auto_secret = bool(SENSITIVE_PATTERNS.search(key))
    store[key] = {"value": value, "secret": is_secret or auto_secret}
    return {"set": True, "key": key, "secret": store[key]["secret"]}


def get_env_vars(store: dict, unmask: bool = False) -> list[dict]:
    result = []
    for k, v in sorted(store.items()):
        display = v["value"] if unmask or not v["secret"] else "••••••••"
        result.append({"key": k, "value": display, "secret": v["secret"]})
    return result


def delete_env_var(store: dict, key: str) -> dict:
    if key in store:
        del store[key]
        return {"deleted": True, "key": key}
    return {"deleted": False, "error": "not_found"}


def validate_env(store: dict, required: list[str]) -> dict:
    missing = [k for k in required if k not in store]
    return {"valid": len(missing) == 0, "missing": missing,
            "total": len(store), "required_count": len(required)}
