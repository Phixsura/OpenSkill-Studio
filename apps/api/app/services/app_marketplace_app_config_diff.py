"""Config diff — compare configurations between environments."""


def diff_configs(*, env_a: str, config_a: dict, env_b: str, config_b: dict) -> dict:
    all_keys = sorted(set(list(config_a.keys()) + list(config_b.keys())))
    diffs = []
    same = 0
    for key in all_keys:
        in_a = key in config_a
        in_b = key in config_b
        if in_a and in_b:
            if config_a[key] == config_b[key]:
                same += 1
            else:
                diffs.append({"key": key, "type": "changed",
                              env_a: config_a[key], env_b: config_b[key]})
        elif in_a:
            diffs.append({"key": key, "type": "removed", env_a: config_a[key]})
        else:
            diffs.append({"key": key, "type": "added", env_b: config_b[key]})
    return {
        "env_a": env_a, "env_b": env_b,
        "diffs": diffs, "diff_count": len(diffs),
        "same_count": same, "total_keys": len(all_keys),
        "drift_pct": round(len(diffs) / max(len(all_keys), 1) * 100, 1),
    }
