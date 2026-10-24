"""API contract registry — register and version API contracts."""
from __future__ import annotations


class ContractRegistry:
    def __init__(self):
        self._contracts: dict[str, list[dict]] = {}

    def register(self, name: str, version: str, schema: dict, owner: str = "") -> dict:
        self._contracts.setdefault(name, [])
        entry = {"version": version, "schema": schema, "owner": owner}
        self._contracts[name].append(entry)
        return {"name": name, "version": version, "registered": True}

    def latest(self, name: str) -> dict | None:
        versions = self._contracts.get(name, [])
        return versions[-1] if versions else None

    def versions(self, name: str) -> list[str]:
        return [v["version"] for v in self._contracts.get(name, [])]

    def search(self, query: str = "") -> list[dict]:
        results = []
        for name, versions in self._contracts.items():
            if query and query.lower() not in name.lower():
                continue
            results.append({"name": name, "versions": len(versions),
                            "latest": versions[-1]["version"] if versions else ""})
        return sorted(results, key=lambda r: r["name"])

    def stats(self) -> dict:
        total_versions = sum(len(v) for v in self._contracts.values())
        return {"contracts": len(self._contracts), "total_versions": total_versions}
