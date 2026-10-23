"""SLA tracker — monitor service level agreement compliance."""
from __future__ import annotations


def define_sla(name: str, target_pct: float, metric: str, window_days: int = 30) -> dict:
    return {"name": name, "target_pct": target_pct, "metric": metric, "window_days": window_days}


def check_sla(sla: dict, actual_pct: float) -> dict:
    met = actual_pct >= sla["target_pct"]
    gap = round(actual_pct - sla["target_pct"], 3)
    budget_remaining = round(actual_pct - sla["target_pct"], 3) if met else 0
    status = "met" if met else "breached"
    return {"name": sla["name"], "target": sla["target_pct"], "actual": actual_pct,
            "met": met, "status": status, "gap": gap,
            "budget_remaining": budget_remaining}


def summarize_slas(results: list[dict]) -> dict:
    met_count = sum(1 for r in results if r["met"])
    total = len(results)
    breached = [r["name"] for r in results if not r["met"]]
    return {"total": total, "met": met_count, "breached_count": total - met_count,
            "breached_names": breached,
            "compliance_pct": round(met_count / max(total, 1) * 100)}
