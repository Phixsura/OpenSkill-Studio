"""Fleet WASM — track WebAssembly runtime health."""
from __future__ import annotations
def fleet_wasm_status(modules: list[dict]) -> dict:
    loaded = [m for m in modules if m.get("loaded", True)]
    total_exec = sum(m.get("executions_24h", 0) for m in modules)
    avg_exec_ms = round(sum(m.get("avg_exec_ms", 0) for m in modules) / max(len(modules), 1), 1)
    return {"modules": len(modules), "loaded": len(loaded), "executions_24h": total_exec,
            "avg_exec_ms": avg_exec_ms, "performant": avg_exec_ms < 10}
