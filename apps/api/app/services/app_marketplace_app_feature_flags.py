"""Feature flags — per-installation feature toggles for gradual rollout."""

import hashlib


def create_flag(*, app_id: str, key: str, description: str, default_value: bool = False,
                  rollout_pct: int = 0) -> dict:
    if not key or " " in key:
        return {"error": "Key must be non-empty with no spaces"}
    if rollout_pct < 0 or rollout_pct > 100:
        return {"error": "Rollout percentage must be 0-100"}
    return {"app_id": app_id, "key": key, "description": description,
            "default_value": default_value, "rollout_pct": rollout_pct, "error": None}


def evaluate_flag(*, flag: dict, installation_id: str) -> bool:
    if flag.get("rollout_pct", 0) == 100:
        return True
    if flag.get("rollout_pct", 0) == 0:
        return flag.get("default_value", False)
    h = int(hashlib.md5(f"{flag['key']}:{installation_id}".encode()).hexdigest(), 16)
    bucket = h % 100
    return bucket < flag["rollout_pct"]


def list_flags_status(*, flags: list[dict], installation_id: str) -> list[dict]:
    return [{"key": f["key"], "description": f.get("description", ""),
             "enabled": evaluate_flag(flag=f, installation_id=installation_id),
             "rollout_pct": f.get("rollout_pct", 0)} for f in flags]
