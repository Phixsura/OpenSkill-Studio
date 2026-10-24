"""Cluster node manager — manage cluster node lifecycle."""
from __future__ import annotations


class ClusterNodeManager:
    def __init__(self):
        self._nodes: dict[str, dict] = {}

    def add_node(self, name: str, role: str, cpu: int, memory_gb: int) -> dict:
        self._nodes[name] = {"name": name, "role": role, "cpu": cpu,
                              "memory_gb": memory_gb, "status": "ready",
                              "pods": 0, "cordon": False}
        return self._nodes[name]

    def cordon(self, name: str) -> dict:
        self._nodes[name]["cordon"] = True
        return {"name": name, "cordoned": True}

    def drain(self, name: str) -> dict:
        node = self._nodes[name]
        node["pods"] = 0
        node["status"] = "drained"
        return {"name": name, "status": "drained"}

    def remove(self, name: str) -> dict:
        del self._nodes[name]
        return {"name": name, "removed": True}

    def stats(self) -> dict:
        total_cpu = sum(n["cpu"] for n in self._nodes.values())
        total_mem = sum(n["memory_gb"] for n in self._nodes.values())
        ready = sum(1 for n in self._nodes.values() if n["status"] == "ready")
        return {"total_nodes": len(self._nodes), "ready": ready,
                "total_cpu": total_cpu, "total_memory_gb": total_mem}
