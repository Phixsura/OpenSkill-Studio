"""Fleet Zookeeper — track coordination service health."""
from __future__ import annotations
def fleet_zookeeper_status(nodes: list[dict]) -> dict:
    followers = [n for n in nodes if n.get("role") == "follower"]
    leader = [n for n in nodes if n.get("role") == "leader"]
    avg_latency = round(sum(n.get("avg_latency_ms", 0) for n in nodes) / max(len(nodes), 1), 1)
    return {"nodes": len(nodes), "leader": len(leader), "followers": len(followers),
            "avg_latency_ms": avg_latency, "quorum": len(leader) == 1}
