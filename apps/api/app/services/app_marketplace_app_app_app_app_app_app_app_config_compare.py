"""Config comparison tool — compare configs across environments."""
from __future__ import annotations


def compare_configs(configs: dict[str, dict]) -> dict:
    env_names = list(configs.keys())
    all_keys = set()
    for cfg in configs.values():
        all_keys.update(cfg.keys())
    diffs = []
    same = []
    for key in sorted(all_keys):
        values = {env: configs[env].get(key, "<missing>") for env in env_names}
        unique_vals = set(str(v) for v in values.values())
        if len(unique_vals) == 1:
            same.append(key)
        else:
            diffs.append({"key": key, "values": values})
    return {"environments": env_names, "total_keys": len(all_keys),
            "same_count": len(same), "diff_count": len(diffs), "diffs": diffs,
            "identical": len(diffs) == 0}
