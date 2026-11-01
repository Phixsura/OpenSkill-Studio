"""Service mesh fault injection — inject faults between mesh services."""
from __future__ import annotations
import hashlib


class MeshFaultInjector:
    def __init__(self):
        self._rules: list[dict] = []

    def add_rule(self, source: str, destination: str, fault_type: str,
                 percentage: int = 100, config: dict | None = None) -> dict:
        rule = {"source": source, "destination": destination,
                "fault_type": fault_type, "percentage": percentage,
                "config": config or {}, "active": True}
        self._rules.append(rule)
        return {"added": True, "total_rules": len(self._rules)}

    def should_inject(self, source: str, destination: str, request_id: str) -> dict:
        for rule in self._rules:
            if not rule["active"]:
                continue
            if rule["source"] != source or rule["destination"] != destination:
                continue
            h = int(hashlib.md5(request_id.encode()).hexdigest()[:8], 16) % 100
            if h < rule["percentage"]:
                return {"inject": True, "fault_type": rule["fault_type"],
                        "config": rule["config"]}
        return {"inject": False}

    def disable_all(self) -> dict:
        count = sum(1 for r in self._rules if r["active"])
        for r in self._rules:
            r["active"] = False
        return {"disabled": count}

    def stats(self) -> dict:
        active = sum(1 for r in self._rules if r["active"])
        return {"total_rules": len(self._rules), "active": active}
