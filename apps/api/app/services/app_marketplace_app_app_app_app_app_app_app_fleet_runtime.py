"""Fleet container runtime — track runtime distribution."""
from __future__ import annotations
def fleet_container_runtime(nodes: list[dict]) -> dict:
    runtimes: dict[str, int] = {}
    for n in nodes:
        rt = n.get("runtime", "unknown")
        runtimes[rt] = runtimes.get(rt, 0) + 1
    return {"total": len(nodes), "runtimes": runtimes, "heterogeneous": len(runtimes) > 1}
