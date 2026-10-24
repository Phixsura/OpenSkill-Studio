"""Service mesh telemetry — aggregate cross-service communication metrics."""
from __future__ import annotations


def aggregate_mesh_traffic(connections: list[dict]) -> dict:
    by_pair: dict[str, dict] = {}
    for c in connections:
        key = f"{c['source']}→{c['destination']}"
        if key not in by_pair:
            by_pair[key] = {"source": c["source"], "destination": c["destination"],
                             "requests": 0, "errors": 0, "total_latency_ms": 0}
        by_pair[key]["requests"] += c.get("requests", 1)
        by_pair[key]["errors"] += c.get("errors", 0)
        by_pair[key]["total_latency_ms"] += c.get("latency_ms", 0)
    results = []
    for key, data in by_pair.items():
        avg_lat = round(data["total_latency_ms"] / max(data["requests"], 1), 1)
        err_rate = round(data["errors"] / max(data["requests"], 1) * 100, 1)
        results.append({**data, "avg_latency_ms": avg_lat, "error_rate_pct": err_rate})
    total_req = sum(r["requests"] for r in results)
    total_err = sum(r["errors"] for r in results)
    return {"connections": sorted(results, key=lambda r: -r["requests"]),
            "total_requests": total_req, "total_errors": total_err,
            "unique_pairs": len(results),
            "mesh_error_rate": round(total_err / max(total_req, 1) * 100, 2)}
