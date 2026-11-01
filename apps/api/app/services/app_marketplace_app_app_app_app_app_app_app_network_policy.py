"""Network policy manager — define ingress/egress rules for service isolation."""
from __future__ import annotations


class NetworkPolicyManager:
    def __init__(self):
        self._policies: dict[str, dict] = {}

    def create_policy(self, name: str, *, target: str,
                       ingress: list[dict] | None = None,
                       egress: list[dict] | None = None) -> dict:
        self._policies[name] = {
            "name": name, "target": target,
            "ingress": ingress or [], "egress": egress or [],
            "enabled": True,
        }
        return {"name": name, "target": target, "status": "created"}

    def check_allowed(self, *, source: str, destination: str, port: int) -> dict:
        for p in self._policies.values():
            if not p["enabled"]:
                continue
            if p["target"] == destination:
                for rule in p["ingress"]:
                    if rule.get("from") == source and port in rule.get("ports", []):
                        return {"allowed": True, "policy": p["name"], "direction": "ingress"}
            if p["target"] == source:
                for rule in p["egress"]:
                    if rule.get("to") == destination and port in rule.get("ports", []):
                        return {"allowed": True, "policy": p["name"], "direction": "egress"}
        return {"allowed": False, "reason": "no_matching_policy"}

    def summary(self) -> dict:
        total_rules = sum(len(p["ingress"]) + len(p["egress"]) for p in self._policies.values())
        return {"total_policies": len(self._policies), "total_rules": total_rules,
                "policies": [{"name": p["name"], "target": p["target"],
                              "ingress_count": len(p["ingress"]), "egress_count": len(p["egress"]),
                              "enabled": p["enabled"]} for p in self._policies.values()]}
