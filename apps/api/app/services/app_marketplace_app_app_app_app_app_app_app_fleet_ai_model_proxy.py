"""Fleet AI Model Proxy — track transparent AI model request proxying."""
from __future__ import annotations
def fleet_ai_model_proxy(proxies: list[dict]) -> dict:
    active = [p for p in proxies if p.get("active", True)]
    requests_24h = sum(p.get("requests_24h", 0) for p in proxies)
    models_proxied = sum(p.get("models", 0) for p in proxies)
    overhead_ms = round(sum(p.get("overhead_ms", 0) for p in proxies) / max(len(proxies), 1), 1)
    return {"proxies": len(proxies), "active": len(active), "requests_24h": requests_24h,
            "models": models_proxied, "overhead_ms": overhead_ms, "transparent": overhead_ms < 5}
