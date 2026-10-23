"""Release train manager — coordinate multi-service releases."""
from __future__ import annotations
import secrets


class ReleaseTrainManager:
    def __init__(self):
        self._trains: dict[str, dict] = {}

    def create_train(self, *, version: str, services: list[dict],
                      target_date: str = "") -> dict:
        tid = f"rt_{secrets.token_hex(4)}"
        items = [{"service": s["name"], "version": s.get("version", ""),
                   "status": "pending", "tests_passed": False}
                  for s in services]
        self._trains[tid] = {"id": tid, "version": version,
                              "target_date": target_date, "items": items,
                              "status": "planning"}
        return {"id": tid, "version": version, "services": len(items)}

    def approve_service(self, tid: str, service: str) -> dict:
        train = self._trains.get(tid)
        if not train:
            return {"error": "Train not found"}
        for item in train["items"]:
            if item["service"] == service:
                item["status"] = "approved"
                item["tests_passed"] = True
                break
        all_approved = all(i["status"] == "approved" for i in train["items"])
        if all_approved:
            train["status"] = "ready"
        return {"service": service, "status": "approved",
                "train_ready": all_approved}

    def release(self, tid: str) -> dict:
        train = self._trains.get(tid)
        if not train:
            return {"error": "Train not found"}
        if train["status"] != "ready":
            return {"error": "Train not ready — not all services approved"}
        train["status"] = "released"
        for item in train["items"]:
            item["status"] = "released"
        return {"id": tid, "version": train["version"], "status": "released",
                "services_released": len(train["items"])}

    def status(self, tid: str) -> dict:
        train = self._trains.get(tid)
        if not train:
            return {"error": "Train not found"}
        approved = sum(1 for i in train["items"] if i["status"] in ("approved", "released"))
        return {"id": tid, "version": train["version"], "status": train["status"],
                "approved": approved, "total": len(train["items"]),
                "items": train["items"]}
