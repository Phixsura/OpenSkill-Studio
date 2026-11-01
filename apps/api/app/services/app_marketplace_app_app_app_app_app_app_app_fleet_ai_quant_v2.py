"""Fleet AI Quantizer v2 — track advanced model quantization."""
from __future__ import annotations
def fleet_ai_quantizer_v2(quantizers: list[dict]) -> dict:
    active = [q for q in quantizers if q.get("active", True)]
    models = sum(q.get("models", 0) for q in quantizers)
    bits = min((q.get("bits", 32) for q in quantizers), default=32)
    speedup = round(sum(q.get("speedup_x", 0) for q in quantizers) / max(len(quantizers), 1), 1)
    quality_loss = round(sum(q.get("loss_pct", 0) for q in quantizers) / max(len(quantizers), 1), 2)
    return {"quantizers": len(quantizers), "active": len(active), "models": models,
            "bits": bits, "speedup_x": speedup, "loss_pct": quality_loss, "efficient": speedup > 2 and quality_loss < 1}
