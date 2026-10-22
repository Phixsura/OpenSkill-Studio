"""Environment config — manage per-environment (dev/staging/prod) app settings."""

VALID_ENVS = {"development", "staging", "production"}


def create_env_config(*, app_id: str, environment: str, config: dict) -> dict:
    if environment not in VALID_ENVS:
        return {"error": f"Invalid environment. Use: {', '.join(sorted(VALID_ENVS))}"}
    return {"app_id": app_id, "environment": environment, "config": config, "error": None}


def merge_configs(*, base: dict, override: dict) -> dict:
    merged = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            merged[k] = merge_configs(base=merged[k], override=v)
        else:
            merged[k] = v
    return merged


def get_effective_config(*, base_config: dict, env_overrides: dict, environment: str) -> dict:
    overrides = env_overrides.get(environment, {})
    return merge_configs(base=base_config, override=overrides)


def diff_env_configs(*, env_a: dict, env_b: dict) -> dict:
    all_keys = set(env_a.keys()) | set(env_b.keys())
    diffs = []
    for k in sorted(all_keys):
        a_val = env_a.get(k)
        b_val = env_b.get(k)
        if a_val != b_val:
            diffs.append({"key": k, "env_a": a_val, "env_b": b_val})
    return {"differences": diffs, "count": len(diffs)}
