"""Feature flag manager — toggle features per environment."""
from __future__ import annotations


def evaluate_flags(flags: list[dict], env: str = "production", user_pct: float = 100.0) -> dict:
    results = []
    enabled_count = 0
    for f in flags:
        envs = f.get("environments", ["production", "staging", "development"])
        rollout = f.get("rollout_pct", 100.0)
        active = env in envs and user_pct <= rollout and f.get("enabled", True)
        results.append({
            "key": f["key"],
            "label": f.get("label", f["key"]),
            "enabled": active,
            "rollout_pct": rollout,
            "environments": envs,
        })
        if active:
            enabled_count += 1
    return {"flags": results, "total": len(results), "enabled": enabled_count,
            "disabled": len(results) - enabled_count,
            "environment": env}


def is_flag_on(flags: list[dict], key: str, env: str = "production") -> bool:
    for f in flags:
        if f["key"] == key:
            envs = f.get("environments", ["production", "staging", "development"])
            return env in envs and f.get("enabled", True)
    return False
