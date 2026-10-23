"""API changelog diff — compare two API versions and list changes."""
from __future__ import annotations


def diff_versions(v1_endpoints: list[dict], v2_endpoints: list[dict]) -> dict:
    v1_map = {f"{e['method']}:{e['path']}": e for e in v1_endpoints}
    v2_map = {f"{e['method']}:{e['path']}": e for e in v2_endpoints}
    added = [v2_map[k] for k in v2_map if k not in v1_map]
    removed = [v1_map[k] for k in v1_map if k not in v2_map]
    changed = []
    for k in v1_map:
        if k in v2_map and v1_map[k] != v2_map[k]:
            changed.append({"endpoint": k, "v1": v1_map[k], "v2": v2_map[k]})
    return {
        "added": [{"method": e["method"], "path": e["path"]} for e in added],
        "removed": [{"method": e["method"], "path": e["path"]} for e in removed],
        "changed": [{"endpoint": c["endpoint"]} for c in changed],
        "added_count": len(added), "removed_count": len(removed),
        "changed_count": len(changed),
        "breaking": len(removed) > 0,
        "summary": f"+{len(added)} -{len(removed)} ~{len(changed)}",
    }
