"""Fleet Firebase — track Google BaaS platform."""
from __future__ import annotations
def fleet_firebase_status(projects: list[dict]) -> dict:
    active = [p for p in projects if p.get("active", True)]
    auth_users = sum(p.get("auth_users", 0) for p in projects)
    firestore_docs = sum(p.get("firestore_docs", 0) for p in projects)
    storage_gb = sum(p.get("storage_gb", 0) for p in projects)
    return {"projects": len(projects), "active": len(active), "auth_users": auth_users,
            "firestore_docs": firestore_docs, "storage_gb": round(storage_gb, 1)}
