"""Fleet DSPy — track programmatic LLM pipeline optimization."""
from __future__ import annotations
def fleet_dspy_status(programs: list[dict]) -> dict:
    deployed = [p for p in programs if p.get("deployed", True)]
    modules = sum(p.get("modules", 0) for p in programs)
    optimizations = sum(p.get("optimizations_24h", 0) for p in programs)
    return {"programs": len(programs), "deployed": len(deployed), "modules": modules,
            "optimizations_24h": optimizations, "all_deployed": len(deployed) == len(programs)}
