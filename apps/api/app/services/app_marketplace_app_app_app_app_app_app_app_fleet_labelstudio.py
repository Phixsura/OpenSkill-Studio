"""Fleet Label Studio — track data labeling platform."""
from __future__ import annotations
def fleet_labelstudio_status(instances: list[dict]) -> dict:
    running = [i for i in instances if i.get("running", True)]
    projects = sum(i.get("projects", 0) for i in instances)
    annotations = sum(i.get("annotations", 0) for i in instances)
    return {"instances": len(instances), "running": len(running), "projects": projects,
            "annotations": annotations, "all_running": len(running) == len(instances)}
