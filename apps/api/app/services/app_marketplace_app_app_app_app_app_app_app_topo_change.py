"""Service topology change tracker — detect topology changes over time."""
from __future__ import annotations


def detect_changes(old_services: list[str], new_services: list[str],
                     old_connections: list[str], new_connections: list[str]) -> dict:
    svc_added = sorted(set(new_services) - set(old_services))
    svc_removed = sorted(set(old_services) - set(new_services))
    conn_added = sorted(set(new_connections) - set(old_connections))
    conn_removed = sorted(set(old_connections) - set(new_connections))
    total = len(svc_added) + len(svc_removed) + len(conn_added) + len(conn_removed)
    return {"services_added": svc_added, "services_removed": svc_removed,
            "connections_added": conn_added, "connections_removed": conn_removed,
            "total_changes": total, "has_changes": total > 0,
            "breaking": len(svc_removed) > 0 or len(conn_removed) > 0}
