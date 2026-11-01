"""Fleet AI Inference Profiler — track per-request latency breakdown."""
from __future__ import annotations
def fleet_ai_inference_profiler(profilers: list[dict]) -> dict:
    active = [p for p in profilers if p.get("active", True)]
    profiles_24h = sum(p.get("profiles_24h", 0) for p in profilers)
    avg_tokenize_ms = round(sum(p.get("tokenize_ms", 0) for p in profilers) / max(len(profilers), 1), 1)
    avg_inference_ms = round(sum(p.get("inference_ms", 0) for p in profilers) / max(len(profilers), 1), 1)
    return {"profilers": len(profilers), "active": len(active), "profiles_24h": profiles_24h,
            "tokenize_ms": avg_tokenize_ms, "inference_ms": avg_inference_ms, "optimized": avg_inference_ms < 100}
