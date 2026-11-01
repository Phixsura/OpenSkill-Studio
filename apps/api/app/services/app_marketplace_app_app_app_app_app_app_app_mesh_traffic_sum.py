"""Mesh traffic summary — unified view of all mesh traffic."""
from __future__ import annotations
from collections import defaultdict


def mesh_traffic_summary(flows: list[dict]) -> dict:
    total_rps = sum(f.get("rps", 0) for f in flows)
    total_errors = sum(f.get("errors", 0) for f in flows)
    total_requests = sum(f.get("requests", 0) for f in flows)
    by_protocol: dict[str, int] = defaultdict(int)
    for f in flows:
        by_protocol[f.get("protocol", "HTTP")] += f.get("requests", 0)
    error_rate = round(total_errors / max(total_requests, 1) * 100, 2)
    top_flows = sorted(flows, key=lambda f: -f.get("rps", 0))[:5]
    return {"total_rps": total_rps, "total_requests": total_requests,
            "total_errors": total_errors, "error_rate_pct": error_rate,
            "by_protocol": dict(by_protocol), "unique_flows": len(flows),
            "top_flows": [{"source": f["source"], "destination": f["destination"],
                            "rps": f["rps"]} for f in top_flows]}
