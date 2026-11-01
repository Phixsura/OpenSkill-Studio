"""Feature flag evaluator — evaluate feature flags with targeting rules."""
from __future__ import annotations
import hashlib


def _hash_pct(user_id: str, flag: str) -> int:
    h = hashlib.sha256(f"{flag}:{user_id}".encode()).hexdigest()
    return int(h[:8], 16) % 100


def evaluate_flag(flag: str, enabled: bool, rollout_pct: int,
                  user_id: str, allowlist: list[str] | None = None,
                  blocklist: list[str] | None = None) -> dict:
    if not enabled:
        return {"flag": flag, "value": False, "reason": "disabled"}
    if blocklist and user_id in blocklist:
        return {"flag": flag, "value": False, "reason": "blocklisted"}
    if allowlist and user_id in allowlist:
        return {"flag": flag, "value": True, "reason": "allowlisted"}
    pct = _hash_pct(user_id, flag)
    in_rollout = pct < rollout_pct
    return {"flag": flag, "value": in_rollout,
            "reason": "rollout" if in_rollout else "outside_rollout",
            "bucket": pct}


def batch_evaluate(flags: list[dict], user_id: str) -> dict:
    results = {}
    for f in flags:
        r = evaluate_flag(f["name"], f.get("enabled", True),
                          f.get("rollout_pct", 100), user_id,
                          f.get("allowlist"), f.get("blocklist"))
        results[f["name"]] = r["value"]
    enabled_count = sum(1 for v in results.values() if v)
    return {"user_id": user_id, "flags": results,
            "total": len(results), "enabled": enabled_count}
