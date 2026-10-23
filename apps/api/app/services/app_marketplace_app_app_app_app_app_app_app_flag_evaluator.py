"""Feature flag evaluator — evaluate flags with user targeting rules."""
from __future__ import annotations
import hashlib


class FlagEvaluator:
    def __init__(self):
        self._flags: dict[str, dict] = {}

    def define(self, key: str, *, default: bool = False, rollout_pct: int = 0,
               target_users: list[str] | None = None,
               target_orgs: list[str] | None = None) -> dict:
        self._flags[key] = {"key": key, "default": default,
                             "rollout_pct": rollout_pct,
                             "target_users": set(target_users or []),
                             "target_orgs": set(target_orgs or [])}
        return {"defined": key}

    def evaluate(self, key: str, *, user_id: str = "", org_id: str = "") -> dict:
        flag = self._flags.get(key)
        if not flag:
            return {"enabled": False, "reason": "flag_not_found"}
        if user_id in flag["target_users"]:
            return {"enabled": True, "reason": "user_targeted"}
        if org_id in flag["target_orgs"]:
            return {"enabled": True, "reason": "org_targeted"}
        if flag["rollout_pct"] > 0 and user_id:
            bucket = int(hashlib.md5(f"{key}:{user_id}".encode()).hexdigest()[:8], 16) % 100
            if bucket < flag["rollout_pct"]:
                return {"enabled": True, "reason": "rollout"}
        return {"enabled": flag["default"], "reason": "default"}

    def list_flags(self) -> list[dict]:
        return [{"key": f["key"], "default": f["default"], "rollout_pct": f["rollout_pct"],
                 "targeted_users": len(f["target_users"]), "targeted_orgs": len(f["target_orgs"])}
                for f in self._flags.values()]
