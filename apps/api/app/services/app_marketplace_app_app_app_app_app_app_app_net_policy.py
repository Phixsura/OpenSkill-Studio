"""Network policy manager — define and evaluate network access policies."""
from __future__ import annotations


class NetworkPolicyManager:
    def __init__(self):
        self._policies: list[dict] = []

    def add_policy(self, name: str, source: str, destination: str,
                   port: int, protocol: str = "TCP", action: str = "allow") -> dict:
        policy = {"name": name, "source": source, "destination": destination,
                  "port": port, "protocol": protocol, "action": action}
        self._policies.append(policy)
        return {"added": True, "total_policies": len(self._policies)}

    def evaluate(self, source: str, destination: str, port: int, protocol: str = "TCP") -> dict:
        for p in self._policies:
            src_match = p["source"] in (source, "*")
            dst_match = p["destination"] in (destination, "*")
            port_match = p["port"] == port or p["port"] == 0
            proto_match = p["protocol"] == protocol
            if src_match and dst_match and port_match and proto_match:
                return {"allowed": p["action"] == "allow", "matched_policy": p["name"],
                        "action": p["action"]}
        return {"allowed": False, "matched_policy": None, "action": "implicit_deny"}

    def list_policies(self) -> list[dict]:
        return list(self._policies)

    def stats(self) -> dict:
        allow_count = sum(1 for p in self._policies if p["action"] == "allow")
        return {"total": len(self._policies), "allow": allow_count,
                "deny": len(self._policies) - allow_count}
