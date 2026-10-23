"""Kubernetes pod health — monitor pod status, restarts, and resource usage."""
from __future__ import annotations


def analyze_pods(pods: list[dict]) -> dict:
    running = [p for p in pods if p.get("status") == "Running"]
    pending = [p for p in pods if p.get("status") == "Pending"]
    failed = [p for p in pods if p.get("status") in ("Failed", "CrashLoopBackOff", "Error")]
    total_restarts = sum(p.get("restarts", 0) for p in pods)
    high_restart = [p for p in pods if p.get("restarts", 0) >= 5]
    avg_cpu = round(sum(p.get("cpu_pct", 0) for p in running) / max(len(running), 1), 1)
    avg_mem = round(sum(p.get("mem_pct", 0) for p in running) / max(len(running), 1), 1)
    health = "healthy" if not failed and not high_restart else \
             "degraded" if running else "down"
    return {
        "total": len(pods), "running": len(running), "pending": len(pending),
        "failed": len(failed), "total_restarts": total_restarts,
        "high_restart_pods": len(high_restart), "avg_cpu_pct": avg_cpu,
        "avg_mem_pct": avg_mem, "health": health,
        "pods": [{"name": p["name"], "status": p.get("status", "Unknown"),
                  "restarts": p.get("restarts", 0), "cpu_pct": p.get("cpu_pct", 0),
                  "mem_pct": p.get("mem_pct", 0)} for p in pods],
    }
