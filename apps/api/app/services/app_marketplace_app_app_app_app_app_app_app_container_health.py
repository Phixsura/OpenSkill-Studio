"""Container health checker — monitor container runtime health."""
from __future__ import annotations


def check_container(name: str, cpu_pct: float, memory_mb: int, memory_limit_mb: int,
                     restart_count: int, status: str = "running") -> dict:
    mem_pct = round(memory_mb / max(memory_limit_mb, 1) * 100, 1)
    oom_risk = mem_pct > 85
    healthy = status == "running" and not oom_risk and restart_count < 5 and cpu_pct < 95
    issues = []
    if oom_risk:
        issues.append("OOM risk — memory above 85%")
    if restart_count >= 5:
        issues.append(f"CrashLoopBackOff risk — {restart_count} restarts")
    if cpu_pct > 95:
        issues.append("CPU throttled")
    return {"name": name, "status": status, "cpu_pct": cpu_pct,
            "memory_mb": memory_mb, "memory_limit_mb": memory_limit_mb,
            "memory_pct": mem_pct, "restart_count": restart_count,
            "healthy": healthy, "issues": issues}


def cluster_health(containers: list[dict]) -> dict:
    healthy = sum(1 for c in containers if c["healthy"])
    total_cpu = round(sum(c["cpu_pct"] for c in containers) / max(len(containers), 1), 1)
    total_restarts = sum(c["restart_count"] for c in containers)
    return {"total": len(containers), "healthy": healthy, "unhealthy": len(containers) - healthy,
            "avg_cpu": total_cpu, "total_restarts": total_restarts}
