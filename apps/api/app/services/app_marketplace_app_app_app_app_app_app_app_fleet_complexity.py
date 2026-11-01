"""Fleet cognitive complexity — track codebase complexity."""
from __future__ import annotations
def fleet_cognitive_complexity(modules: list[dict]) -> dict:
    total = sum(m.get("complexity", 0) for m in modules)
    avg = round(total / max(len(modules), 1), 1)
    high = [m for m in modules if m.get("complexity", 0) > 20]
    return {"modules": len(modules), "total_complexity": total, "avg_complexity": avg,
            "high_complexity": len(high), "maintainable": avg <= 15}
