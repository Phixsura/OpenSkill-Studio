"""Fleet TensorRT — track GPU-optimized inference."""
from __future__ import annotations
def fleet_tensorrt_status(engines: list[dict]) -> dict:
    active = [e for e in engines if e.get("active", True)]
    throughput = sum(e.get("throughput_inf_per_sec", 0) for e in engines)
    latency_ms = round(sum(e.get("p99_ms", 0) for e in engines) / max(len(engines), 1), 1)
    return {"engines": len(engines), "active": len(active), "throughput": throughput,
            "p99_ms": latency_ms, "optimized": latency_ms < 10}
