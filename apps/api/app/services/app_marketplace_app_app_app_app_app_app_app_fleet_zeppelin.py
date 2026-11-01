"""Fleet Zeppelin — track interactive analytics notebook."""
from __future__ import annotations
def fleet_zeppelin_status(instances: list[dict]) -> dict:
    running = [i for i in instances if i.get("running", True)]
    notebooks = sum(i.get("notebooks", 0) for i in instances)
    interpreters = sum(i.get("interpreters", 0) for i in instances)
    return {"instances": len(instances), "running": len(running), "notebooks": notebooks,
            "interpreters": interpreters, "all_running": len(running) == len(instances)}
