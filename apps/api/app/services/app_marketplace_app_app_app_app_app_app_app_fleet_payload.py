"""Fleet Payload — track headless CMS health."""
from __future__ import annotations
def fleet_payload_status(instances: list[dict]) -> dict:
    running = [i for i in instances if i.get("running", True)]
    collections = sum(i.get("collections", 0) for i in instances)
    documents = sum(i.get("documents", 0) for i in instances)
    return {"instances": len(instances), "running": len(running), "collections": collections,
            "documents": documents, "healthy": len(running) == len(instances)}
