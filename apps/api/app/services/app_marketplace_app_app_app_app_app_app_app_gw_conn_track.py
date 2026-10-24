"""Gateway connection tracker — track active gateway connections."""
from __future__ import annotations
from collections import defaultdict


def track_connections(connections: list[dict]) -> dict:
    by_client: dict[str, int] = defaultdict(int)
    by_protocol: dict[str, int] = defaultdict(int)
    active = 0
    for c in connections:
        if c.get("state") == "active":
            active += 1
            by_client[c.get("client_ip", "unknown")] += 1
            by_protocol[c.get("protocol", "HTTP/1.1")] += 1
    top_clients = sorted(by_client.items(), key=lambda x: -x[1])[:5]
    return {"total_connections": len(connections), "active": active,
            "by_protocol": dict(by_protocol),
            "top_clients": [{"ip": k, "count": v} for k, v in top_clients],
            "unique_clients": len(by_client)}
