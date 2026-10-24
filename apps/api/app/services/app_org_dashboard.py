"""Org dashboard — compile app installation data for org admins."""


def build_org_dashboard(*, installations: list[dict], total_executions: int = 0,
                         total_errors: int = 0, pending_upgrades: int = 0) -> dict:
    active = [i for i in installations if i.get("status") == "active"]
    categories = {}
    for i in active:
        cat = i.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    error_rate = round(total_errors / total_executions * 100, 1) if total_executions > 0 else 0
    return {
        "total_installed": len(installations),
        "active": len(active),
        "by_category": categories,
        "total_executions": total_executions,
        "error_rate": error_rate,
        "pending_upgrades": pending_upgrades,
        "health": "healthy" if error_rate < 5 else "degraded" if error_rate < 15 else "critical",
    }
