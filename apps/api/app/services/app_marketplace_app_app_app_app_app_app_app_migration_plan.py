"""Migration planner — plan data/schema migrations between versions."""
from __future__ import annotations


def plan_migration(current: str, target: str, steps: list[dict]) -> dict:
    applicable = [s for s in steps if s.get("from_version", "") >= current and s.get("to_version", "") <= target]
    total_est = sum(s.get("estimated_sec", 0) for s in applicable)
    has_breaking = any(s.get("breaking", False) for s in applicable)
    has_data_loss = any(s.get("data_loss", False) for s in applicable)
    risk = "high" if has_data_loss else "medium" if has_breaking else "low"
    return {"current": current, "target": target, "steps": applicable,
            "step_count": len(applicable), "estimated_sec": total_est,
            "has_breaking": has_breaking, "has_data_loss": has_data_loss,
            "risk": risk, "requires_downtime": has_breaking or has_data_loss}


def generate_rollback(steps: list[dict]) -> list[dict]:
    return [{"action": f"undo_{s.get('action', 'unknown')}", "table": s.get("table", ""),
             "description": f"Rollback: {s.get('description', '')}"} for s in reversed(steps)]
