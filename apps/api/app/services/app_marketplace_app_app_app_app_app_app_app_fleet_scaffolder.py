"""Fleet Backstage scaffolder — track template execution."""
from __future__ import annotations
def fleet_scaffolder_status(templates: list[dict]) -> dict:
    executed = sum(t.get("executions_30d", 0) for t in templates)
    top = max(templates, key=lambda t: t.get("executions_30d", 0)) if templates else None
    return {"templates": len(templates), "executions_30d": executed,
            "top_template": top.get("name") if top else None, "adopted": executed > 50}
