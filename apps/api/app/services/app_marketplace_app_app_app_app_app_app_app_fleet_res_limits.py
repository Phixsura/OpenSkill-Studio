"""Fleet resource limits — audit containers without resource limits."""
from __future__ import annotations
def fleet_resource_limits(containers: list[dict]) -> dict:
    no_cpu = [c for c in containers if not c.get("has_cpu_limit", True)]
    no_mem = [c for c in containers if not c.get("has_mem_limit", True)]
    return {"total": len(containers), "no_cpu_limit": len(no_cpu),
            "no_mem_limit": len(no_mem), "all_limited": len(no_cpu) == 0 and len(no_mem) == 0}
