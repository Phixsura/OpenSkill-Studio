"""Namespace manager — manage isolated namespaces for multi-tenant workloads."""
from __future__ import annotations


class NamespaceManager:
    def __init__(self):
        self._namespaces: dict[str, dict] = {}

    def create(self, name: str, tenant: str, labels: dict | None = None) -> dict:
        self._namespaces[name] = {"name": name, "tenant": tenant,
                                   "labels": labels or {}, "status": "active",
                                   "resources": 0}
        return self._namespaces[name]

    def delete(self, name: str) -> dict:
        if name in self._namespaces:
            del self._namespaces[name]
            return {"name": name, "deleted": True}
        return {"name": name, "deleted": False}

    def list_by_tenant(self, tenant: str) -> list[dict]:
        return [ns for ns in self._namespaces.values() if ns["tenant"] == tenant]

    def stats(self) -> dict:
        tenants = set(ns["tenant"] for ns in self._namespaces.values())
        return {"total": len(self._namespaces), "tenants": len(tenants)}
