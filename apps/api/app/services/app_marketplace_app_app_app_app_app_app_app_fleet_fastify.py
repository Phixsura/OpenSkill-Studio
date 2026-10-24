"""Fleet Fastify — track high-performance Node.js framework."""
from __future__ import annotations
def fleet_fastify_status(instances: list[dict]) -> dict:
    healthy = [i for i in instances if i.get("healthy", True)]
    total_rps = sum(i.get("rps", 0) for i in instances)
    avg_lat = round(sum(i.get("p95_ms", 0) for i in instances) / max(len(instances), 1), 1)
    return {"instances": len(instances), "healthy": len(healthy), "rps": total_rps,
            "p95_ms": avg_lat, "performant": avg_lat < 50}
