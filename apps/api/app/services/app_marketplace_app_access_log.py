"""Access log — structured access logs for app API usage auditing."""

from datetime import datetime, timezone
from collections import defaultdict


def create_access_log_entry(*, app_id: str, user_id: str, method: str, path: str,
                               status_code: int, ip_address: str, user_agent: str) -> dict:
    return {"app_id": app_id, "user_id": user_id, "method": method, "path": path,
            "status_code": status_code, "ip_address": ip_address, "user_agent": user_agent,
            "timestamp": datetime.now(timezone.utc).isoformat()}


def analyze_access_patterns(*, logs: list[dict]) -> dict:
    by_path = defaultdict(int)
    by_user = defaultdict(int)
    by_status = defaultdict(int)
    for l in logs:
        by_path[l.get("path", "")] += 1
        by_user[l.get("user_id", "")] += 1
        by_status[str(l.get("status_code", 0))] += 1
    return {
        "total_requests": len(logs),
        "unique_users": len(by_user),
        "top_paths": sorted(by_path.items(), key=lambda x: -x[1])[:5],
        "status_distribution": dict(by_status),
    }
