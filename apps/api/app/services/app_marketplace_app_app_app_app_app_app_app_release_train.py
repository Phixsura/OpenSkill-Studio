"""Release train manager — coordinate multi-service releases."""
from __future__ import annotations
import time


def create_train(name: str, services: list[dict], target_date: str) -> dict:
    items = []
    for s in services:
        items.append({"service": s["name"], "version": s["version"],
                       "status": s.get("status", "pending"),
                       "owner": s.get("owner", "unassigned")})
    ready = sum(1 for i in items if i["status"] == "ready")
    return {"name": name, "target_date": target_date, "services": items,
            "total": len(items), "ready": ready,
            "all_ready": ready == len(items),
            "pct_ready": round(ready / max(len(items), 1) * 100)}


def advance_service(train: dict, service_name: str, new_status: str) -> dict:
    for s in train["services"]:
        if s["service"] == service_name:
            s["status"] = new_status
            break
    ready = sum(1 for s in train["services"] if s["status"] == "ready")
    train["ready"] = ready
    train["all_ready"] = ready == train["total"]
    train["pct_ready"] = round(ready / max(train["total"], 1) * 100)
    return train
