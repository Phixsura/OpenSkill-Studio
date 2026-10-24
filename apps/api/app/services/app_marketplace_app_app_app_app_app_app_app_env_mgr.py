"""Platform environment manager — manage deployment environments."""
from __future__ import annotations


class EnvironmentManager:
    def __init__(self):
        self._envs: dict[str, dict] = {}

    def create(self, name: str, tier: str = "standard", region: str = "us-east") -> dict:
        self._envs[name] = {"name": name, "tier": tier, "region": region,
                             "status": "provisioning", "services": []}
        return self._envs[name]

    def provision(self, name: str) -> dict:
        self._envs[name]["status"] = "active"
        return {"name": name, "status": "active"}

    def deploy_service(self, env: str, service: str, version: str) -> dict:
        e = self._envs[env]
        e["services"].append({"service": service, "version": version})
        return {"env": env, "service": service, "version": version, "deployed": True}

    def promote(self, from_env: str, to_env: str) -> dict:
        source = self._envs[from_env]
        target = self._envs[to_env]
        target["services"] = list(source["services"])
        return {"from": from_env, "to": to_env,
                "services_promoted": len(target["services"])}

    def list_envs(self) -> list[dict]:
        return [{"name": e["name"], "tier": e["tier"], "region": e["region"],
                 "status": e["status"], "services": len(e["services"])}
                for e in self._envs.values()]
