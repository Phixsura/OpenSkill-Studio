"""Service mesh observability — observe traffic between mesh services."""
from __future__ import annotations
from collections import defaultdict


def analyze_mesh_traffic(flows: list[dict]) -> dict:
    by_pair: dict[str, dict] = defaultdict(lambda: {"count": 0, "errors": 0, "total_ms": 0})
    for f in flows:
        key = f"{f['source']}→{f['destination']}"
        by_pair[key]["count"] += 1
        by_pair[key]["total_ms"] += f.get("latency_ms", 0)
        if f.get("status", 200) >= 400:
            by_pair[key]["errors"] += 1
    pairs = []
    for key, data in sorted(by_pair.items(), key=lambda x: -x[1]["count"]):
        avg = round(data["total_ms"] / max(data["count"], 1), 1)
        err_rate = round(data["errors"] / max(data["count"], 1) * 100, 1)
        src, dst = key.split("→")
        pairs.append({"source": src, "destination": dst, "count": data["count"],
                       "avg_ms": avg, "error_rate": err_rate})
    return {"pairs": pairs, "total_flows": len(flows),
            "unique_pairs": len(pairs),
            "total_errors": sum(d["errors"] for d in by_pair.values())}
