"""Release gate controller — manage release gates for safe deployments."""
from __future__ import annotations


class ReleaseGateController:
    def __init__(self):
        self._gates: dict[str, list[dict]] = {}

    def define_release(self, release: str, gates: list[dict]) -> dict:
        self._gates[release] = [{"name": g["name"], "required": g.get("required", True),
                                  "passed": False} for g in gates]
        return {"release": release, "gates": len(self._gates[release])}

    def pass_gate(self, release: str, gate_name: str) -> dict:
        for g in self._gates[release]:
            if g["name"] == gate_name:
                g["passed"] = True
                return {"release": release, "gate": gate_name, "passed": True}
        return {"release": release, "gate": gate_name, "error": "gate_not_found"}

    def can_release(self, release: str) -> dict:
        gates = self._gates.get(release, [])
        required_passed = all(g["passed"] for g in gates if g["required"])
        pending = [g["name"] for g in gates if g["required"] and not g["passed"]]
        return {"release": release, "can_release": required_passed,
                "pending_gates": pending, "total_gates": len(gates),
                "passed_gates": sum(1 for g in gates if g["passed"])}
