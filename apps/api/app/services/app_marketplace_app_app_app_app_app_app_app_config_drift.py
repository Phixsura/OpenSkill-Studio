"""Config drift detector — detect config differences across environments."""
from __future__ import annotations


def detect_drift(envs: dict[str, dict]) -> dict:
    if len(envs) < 2:
        return {"drifts": [], "drift_count": 0, "has_drift": False}
    env_names = list(envs.keys())
    all_keys = set()
    for config in envs.values():
        all_keys.update(config.keys())
    drifts = []
    for key in sorted(all_keys):
        values = {env: envs[env].get(key, "<missing>") for env in env_names}
        unique = set(str(v) for v in values.values())
        if len(unique) > 1:
            drifts.append({"key": key, "values": values, "environments": len(unique)})
    return {"drifts": drifts, "drift_count": len(drifts),
            "total_keys": len(all_keys), "has_drift": len(drifts) > 0,
            "environments": env_names}


def suggest_fixes(drifts: list[dict], source_env: str) -> list[dict]:
    fixes = []
    for d in drifts:
        source_val = d["values"].get(source_env)
        if source_val is None:
            continue
        for env, val in d["values"].items():
            if env != source_env and str(val) != str(source_val):
                fixes.append({"key": d["key"], "environment": env,
                              "current": val, "expected": source_val})
    return fixes
