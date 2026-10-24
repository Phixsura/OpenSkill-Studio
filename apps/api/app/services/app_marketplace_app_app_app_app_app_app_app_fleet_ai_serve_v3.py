"""Fleet AI Model Serving v3 — track next-gen model serving infrastructure."""
from __future__ import annotations
def fleet_ai_model_serving_v3(servers: list[dict]) -> dict:
    active = [s for s in servers if s.get("active", True)]
    models = sum(s.get("models", 0) for s in servers)
    rps = sum(s.get("rps", 0) for s in servers)
    p99_ms = round(sum(s.get("p99_ms", 0) for s in servers) / max(len(servers), 1), 1)
    gpu_util = round(sum(s.get("gpu_util", 0) for s in servers) / max(len(servers), 1), 1)
    return {"servers": len(servers), "active": len(active), "models": models,
            "rps": rps, "p99_ms": p99_ms, "gpu_util": gpu_util, "performant": p99_ms < 100}
