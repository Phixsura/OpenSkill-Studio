"""API key usage analytics — track usage per API key."""
from __future__ import annotations
from collections import defaultdict


def analyze_key_usage(requests: list[dict]) -> dict:
    by_key: dict[str, dict] = defaultdict(lambda: {"requests": 0, "errors": 0, "endpoints": set()})
    for r in requests:
        key = r.get("api_key", "anonymous")
        by_key[key]["requests"] += 1
        by_key[key]["endpoints"].add(r.get("endpoint", "/"))
        if r.get("status", 200) >= 400:
            by_key[key]["errors"] += 1
    keys = []
    for key, data in sorted(by_key.items(), key=lambda x: -x[1]["requests"]):
        err_rate = round(data["errors"] / max(data["requests"], 1) * 100, 1)
        keys.append({"key_preview": f"{key[:8]}...", "requests": data["requests"],
                      "unique_endpoints": len(data["endpoints"]),
                      "error_rate": err_rate})
    return {"keys": keys, "total_keys": len(keys), "total_requests": len(requests)}
