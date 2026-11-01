"""Fleet AI Sandbox — track isolated AI execution environments."""
from __future__ import annotations
def fleet_ai_sandbox(sandboxes: list[dict]) -> dict:
    running = [s for s in sandboxes if s.get("running", True)]
    executions_24h = sum(s.get("executions_24h", 0) for s in sandboxes)
    isolated = [s for s in sandboxes if s.get("isolated", True)]
    return {"sandboxes": len(sandboxes), "running": len(running), "executions_24h": executions_24h,
            "isolated": len(isolated), "secure": len(isolated) == len(sandboxes)}
