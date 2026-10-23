"""App crash report — aggregate and display crash analytics."""

import hashlib


def aggregate_crashes(*, app_id: str, crashes: list[dict]) -> dict:
    groups: dict[str, dict] = {}
    for c in crashes:
        sig = hashlib.sha256(c.get("stack_trace", "")[:200].encode()).hexdigest()[:12]
        if sig not in groups:
            groups[sig] = {"signature": sig, "message": c.get("message", "Unknown"),
                           "count": 0, "affected_users": set(), "first_seen": c.get("timestamp"),
                           "last_seen": c.get("timestamp"), "os_list": set()}
        groups[sig]["count"] += 1
        groups[sig]["affected_users"].add(c.get("user_id", "anon"))
        groups[sig]["os_list"].add(c.get("os", "unknown"))
        groups[sig]["last_seen"] = c.get("timestamp")
    result = []
    for g in sorted(groups.values(), key=lambda x: x["count"], reverse=True):
        result.append({**g, "affected_users": len(g["affected_users"]),
                       "os_list": sorted(g["os_list"])})
    crash_free = round((1 - len(set().union(*(g["affected_users"] for g in groups.values() if isinstance(g["affected_users"], set)))) / max(len(crashes), 1)) * 100, 1) if groups else 100.0
    return {"app_id": app_id, "total_crashes": len(crashes),
            "unique_issues": len(result), "groups": result[:20],
            "crash_free_rate": crash_free}
