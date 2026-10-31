"""Fleet AI Model Compiler — track model compilation and optimization."""
from __future__ import annotations
def fleet_ai_model_compiler(compilers: list[dict]) -> dict:
    active = [c for c in compilers if c.get("active", True)]
    models_compiled = sum(c.get("models", 0) for c in compilers)
    speedup = round(sum(c.get("speedup_x", 0) for c in compilers) / max(len(compilers), 1), 1)
    targets = set()
    for c in compilers:
        targets.update(c.get("targets", []))
    return {"compilers": len(compilers), "active": len(active), "models": models_compiled,
            "speedup_x": speedup, "targets": len(targets), "optimized": speedup > 2}
