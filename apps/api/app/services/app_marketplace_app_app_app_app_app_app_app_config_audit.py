"""Config change auditor — audit all configuration changes."""
from __future__ import annotations
import hashlib, time


class ConfigAuditor:
    def __init__(self):
        self._log: list[dict] = []

    def record_change(self, key: str, old_value: str, new_value: str,
                      changed_by: str, env: str = "production") -> dict:
        entry = {"key": key, "old_hash": hashlib.sha256(old_value.encode()).hexdigest()[:12],
                 "new_hash": hashlib.sha256(new_value.encode()).hexdigest()[:12],
                 "changed_by": changed_by, "env": env, "timestamp": time.time()}
        self._log.append(entry)
        return entry

    def query(self, key: str = "", env: str = "", changed_by: str = "",
              limit: int = 50) -> list[dict]:
        results = self._log
        if key:
            results = [r for r in results if r["key"] == key]
        if env:
            results = [r for r in results if r["env"] == env]
        if changed_by:
            results = [r for r in results if r["changed_by"] == changed_by]
        return results[-limit:]

    def stats(self) -> dict:
        by_env: dict[str, int] = {}
        by_user: dict[str, int] = {}
        for entry in self._log:
            by_env[entry["env"]] = by_env.get(entry["env"], 0) + 1
            by_user[entry["changed_by"]] = by_user.get(entry["changed_by"], 0) + 1
        return {"total_changes": len(self._log), "by_env": by_env, "by_user": by_user}
