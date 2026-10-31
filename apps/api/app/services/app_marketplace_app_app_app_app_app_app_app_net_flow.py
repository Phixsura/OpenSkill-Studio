"""Network flow analyzer — analyze service-to-service network flows."""
from __future__ import annotations


def analyze_flows(flows: list[dict]) -> dict:
    by_pair: dict[str, dict] = {}
    total_bytes = 0
    for f in flows:
        key = f"{f['src']}→{f['dst']}"
        if key not in by_pair:
            by_pair[key] = {"src": f["src"], "dst": f["dst"], "bytes": 0, "packets": 0}
        by_pair[key]["bytes"] += f.get("bytes", 0)
        by_pair[key]["packets"] += f.get("packets", 0)
        total_bytes += f.get("bytes", 0)
    top = sorted(by_pair.values(), key=lambda p: -p["bytes"])[:5]
    return {"total_flows": len(flows), "unique_pairs": len(by_pair),
            "total_bytes": total_bytes, "top_flows": top}
