"""Resource lifecycle manager — manage resource creation, update, deletion."""
from __future__ import annotations
import time


class ResourceLifecycleManager:
    def __init__(self):
        self._resources: dict[str, dict] = {}
        self._audit: list[dict] = []

    def create(self, resource_id: str, resource_type: str, owner: str) -> dict:
        self._resources[resource_id] = {"id": resource_id, "type": resource_type,
                                         "owner": owner, "status": "active",
                                         "created_at": time.time(), "version": 1}
        self._audit.append({"action": "create", "resource": resource_id, "by": owner})
        return self._resources[resource_id]

    def update(self, resource_id: str, changes: dict, updated_by: str) -> dict:
        r = self._resources[resource_id]
        r.update(changes)
        r["version"] += 1
        self._audit.append({"action": "update", "resource": resource_id, "by": updated_by})
        return r

    def delete(self, resource_id: str, deleted_by: str) -> dict:
        r = self._resources.pop(resource_id, None)
        if r:
            self._audit.append({"action": "delete", "resource": resource_id, "by": deleted_by})
            return {"deleted": True, "id": resource_id}
        return {"deleted": False}

    def get(self, resource_id: str) -> dict | None:
        return self._resources.get(resource_id)

    def stats(self) -> dict:
        by_type = {}
        for r in self._resources.values():
            by_type[r["type"]] = by_type.get(r["type"], 0) + 1
        return {"total": len(self._resources), "by_type": by_type,
                "audit_entries": len(self._audit)}
