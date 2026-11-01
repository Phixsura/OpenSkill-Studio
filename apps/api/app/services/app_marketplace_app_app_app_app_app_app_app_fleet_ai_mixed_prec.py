"""Fleet AI Mixed Precision — track FP16/BF16/INT8 training and inference."""
from __future__ import annotations
def fleet_ai_mixed_precision(configs: list[dict]) -> dict:
    active = [c for c in configs if c.get("active", True)]
    speedup = round(sum(c.get("speedup_x", 0) for c in configs) / max(len(configs), 1), 1)
    memory_reduction = round(sum(c.get("mem_reduction_pct", 0) for c in configs) / max(len(configs), 1), 1)
    precisions = set()
    for c in configs:
        precisions.update(c.get("precisions", []))
    return {"configs": len(configs), "active": len(active), "speedup_x": speedup,
            "mem_reduction": memory_reduction, "precisions": sorted(precisions), "optimized": speedup > 1.5}
