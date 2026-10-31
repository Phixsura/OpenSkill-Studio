"""Fleet AI Workflow Builder v2 — track visual AI workflow construction."""
from __future__ import annotations
def fleet_ai_workflow_builder_v2(builders: list[dict]) -> dict:
    active = [b for b in builders if b.get("active", True)]
    workflows = sum(b.get("workflows", 0) for b in builders)
    nodes = sum(b.get("nodes", 0) for b in builders)
    executions_24h = sum(b.get("executions_24h", 0) for b in builders)
    return {"builders": len(builders), "active": len(active), "workflows": workflows,
            "nodes": nodes, "executions_24h": executions_24h, "productive": workflows > 10}
