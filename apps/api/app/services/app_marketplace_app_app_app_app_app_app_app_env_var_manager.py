"""Environment variable manager — secure env var storage with masking."""
from __future__ import annotations
import hashlib
import hmac
import secrets

_HMAC_KEY = secrets.token_bytes(32)


def create_env_store() -> dict:
    return {"vars": {}, "count": 0}


def set_var(store: dict, key: str, value: str, *, sensitive: bool = True) -> dict:
    if not key or not key.replace("_", "").isalnum():
        return {"error": "Invalid key — alphanumeric and underscores only"}
    integrity = hmac.new(_HMAC_KEY, value.encode(), hashlib.sha256).hexdigest()[:16]
    store["vars"][key] = {
        "value": value, "sensitive": sensitive,
        "masked": _mask(value) if sensitive else value,
        "integrity": integrity,
    }
    store["count"] = len(store["vars"])
    return {"key": key, "masked": store["vars"][key]["masked"],
            "sensitive": sensitive, "status": "set"}


def get_var(store: dict, key: str, *, unmask: bool = False) -> dict:
    entry = store["vars"].get(key)
    if not entry:
        return {"key": key, "status": "not_found"}
    display = entry["value"] if unmask or not entry["sensitive"] else entry["masked"]
    return {"key": key, "value": display, "sensitive": entry["sensitive"], "status": "found"}


def list_vars(store: dict) -> dict:
    items = [{"key": k, "masked": v["masked"], "sensitive": v["sensitive"]}
             for k, v in sorted(store["vars"].items())]
    return {"count": len(items), "vars": items}


def _mask(val: str) -> str:
    if len(val) <= 4:
        return "****"
    return val[:2] + "*" * (len(val) - 4) + val[-2:]
