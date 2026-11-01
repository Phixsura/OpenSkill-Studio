"""App resource usage — CPU, memory, and bandwidth monitoring."""


def build_resource_usage(*, cpu_pct: float, memory_mb: int, memory_limit_mb: int,
                            bandwidth_mb: int, bandwidth_limit_mb: int,
                            storage_mb: int, storage_limit_mb: int) -> dict:
    def _pct(used: float, limit: float) -> float:
        return round(used / max(limit, 1) * 100, 1)

    def _status(pct: float) -> str:
        return "critical" if pct >= 90 else "warning" if pct >= 75 else "ok"

    mem_pct = _pct(memory_mb, memory_limit_mb)
    bw_pct = _pct(bandwidth_mb, bandwidth_limit_mb)
    st_pct = _pct(storage_mb, storage_limit_mb)

    resources = [
        {"name": "CPU", "icon": "⚡", "value": cpu_pct, "display": f"{cpu_pct}%",
         "status": _status(cpu_pct)},
        {"name": "Memory", "icon": "🧠", "value": mem_pct, "display": f"{memory_mb}/{memory_limit_mb}MB",
         "status": _status(mem_pct)},
        {"name": "Bandwidth", "icon": "📡", "value": bw_pct, "display": f"{bandwidth_mb}/{bandwidth_limit_mb}MB",
         "status": _status(bw_pct)},
        {"name": "Storage", "icon": "💾", "value": st_pct, "display": f"{storage_mb}/{storage_limit_mb}MB",
         "status": _status(st_pct)},
    ]
    any_critical = any(r["status"] == "critical" for r in resources)
    return {"resources": resources, "overall": "critical" if any_critical else "ok"}
