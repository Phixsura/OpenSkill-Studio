"""Service blueprint — define and validate service architecture blueprints."""
from __future__ import annotations


def create_blueprint(name: str, components: list[dict]) -> dict:
    by_type: dict[str, int] = {}
    total_cost = 0
    for c in components:
        ctype = c.get("type", "service")
        by_type[ctype] = by_type.get(ctype, 0) + 1
        total_cost += c.get("estimated_cost", 0)
    return {"name": name, "components": components, "component_count": len(components),
            "by_type": by_type, "estimated_monthly_cost": round(total_cost, 2)}


def validate_blueprint(blueprint: dict) -> dict:
    issues = []
    if blueprint["component_count"] == 0:
        issues.append("Blueprint has no components")
    has_db = any(c.get("type") == "database" for c in blueprint["components"])
    has_cache = any(c.get("type") == "cache" for c in blueprint["components"])
    if not has_db:
        issues.append("No database component — consider adding persistence")
    if not has_cache and blueprint["component_count"] > 3:
        issues.append("No cache — consider adding for performance")
    return {"valid": len(issues) == 0, "issues": issues, "issue_count": len(issues)}
