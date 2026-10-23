"""Config diff — environment config comparison across stages."""

import html


def compare_environments(*, envs: dict[str, dict[str, str]]) -> dict:
    all_keys = sorted(set(k for env in envs.values() for k in env))
    env_names = list(envs.keys())
    rows = []
    mismatches = 0
    for key in all_keys:
        values = {e: envs[e].get(key) for e in env_names}
        unique = set(v for v in values.values() if v is not None)
        is_match = len(unique) <= 1
        missing_in = [e for e in env_names if values[e] is None]
        if not is_match or missing_in:
            mismatches += 1
        rows.append({
            "key": key,
            "values": {e: html.escape(v) if v else None for e, v in values.items()},
            "is_match": is_match and not missing_in,
            "missing_in": missing_in,
        })
    return {"rows": rows, "total_keys": len(all_keys), "environments": env_names,
            "mismatches": mismatches, "in_sync": mismatches == 0}
