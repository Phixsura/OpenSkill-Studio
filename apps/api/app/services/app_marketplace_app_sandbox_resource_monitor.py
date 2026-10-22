"""Sandbox resource monitor — track CPU, memory, and network usage of sandboxed apps."""


def check_resource_usage(*, cpu_pct: float, memory_mb: float, network_kb: float,
                           limits: dict) -> dict:
    violations = []
    if cpu_pct > limits.get("cpu_pct", 80):
        violations.append({"resource": "cpu", "current": cpu_pct, "limit": limits["cpu_pct"]})
    if memory_mb > limits.get("memory_mb", 256):
        violations.append({"resource": "memory", "current": memory_mb, "limit": limits["memory_mb"]})
    if network_kb > limits.get("network_kb", 10240):
        violations.append({"resource": "network", "current": network_kb, "limit": limits["network_kb"]})
    return {
        "healthy": len(violations) == 0, "violations": violations,
        "usage": {"cpu_pct": cpu_pct, "memory_mb": memory_mb, "network_kb": network_kb},
    }


def should_throttle(*, cpu_pct: float, memory_mb: float, threshold: float = 90) -> dict:
    throttle = cpu_pct > threshold or memory_mb > 450
    return {"throttle": throttle, "reason": "CPU" if cpu_pct > threshold else "Memory" if memory_mb > 450 else None}


def build_resource_report(*, samples: list[dict]) -> dict:
    if not samples:
        return {"avg_cpu": 0, "avg_memory": 0, "peak_cpu": 0, "peak_memory": 0}
    cpus = [s.get("cpu_pct", 0) for s in samples]
    mems = [s.get("memory_mb", 0) for s in samples]
    return {
        "avg_cpu": round(sum(cpus) / len(cpus), 1), "peak_cpu": round(max(cpus), 1),
        "avg_memory": round(sum(mems) / len(mems), 1), "peak_memory": round(max(mems), 1),
        "samples": len(samples),
    }
