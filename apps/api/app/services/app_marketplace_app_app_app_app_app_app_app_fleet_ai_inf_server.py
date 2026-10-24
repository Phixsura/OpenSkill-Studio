"""Fleet AI Inference Server — track model serving infrastructure."""
from __future__ import annotations
def fleet_ai_inference_server(servers: list[dict]) -> dict:
    active = [s for s in servers if s.get("healthy", True)]
    total_rps = sum(s.get("rps", 0) for s in servers)
    avg_ttft = round(sum(s.get("ttft_ms", 0) for s in servers) / max(len(servers), 1), 1)
    avg_tps = round(sum(s.get("tokens_per_sec", 0) for s in servers) / max(len(servers), 1))
    return {"servers": len(servers), "healthy": len(active), "rps": total_rps,
            "ttft_ms": avg_ttft, "tokens_per_sec": avg_tps, "performant": avg_ttft < 200}
