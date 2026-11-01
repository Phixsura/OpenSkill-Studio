"""Chaos experiment runner — define and run fault injection experiments."""
from __future__ import annotations
import secrets


class ChaosRunner:
    def __init__(self):
        self._experiments: dict[str, dict] = {}

    def create(self, *, name: str, target: str, fault_type: str,
               duration_sec: int = 60, blast_radius_pct: int = 10) -> dict:
        eid = f"chaos_{secrets.token_hex(4)}"
        self._experiments[eid] = {
            "id": eid, "name": name, "target": target,
            "fault_type": fault_type, "duration_sec": duration_sec,
            "blast_radius_pct": min(blast_radius_pct, 100),
            "status": "created", "result": None,
        }
        return {"id": eid, "name": name, "status": "created"}

    def start(self, eid: str) -> dict:
        exp = self._experiments.get(eid)
        if not exp:
            return {"error": "Experiment not found"}
        exp["status"] = "running"
        return {"id": eid, "status": "running", "fault_type": exp["fault_type"]}

    def complete(self, eid: str, *, success: bool, impact: str = "") -> dict:
        exp = self._experiments.get(eid)
        if not exp:
            return {"error": "Experiment not found"}
        exp["status"] = "completed"
        exp["result"] = {"success": success, "impact": impact,
                          "hypothesis_confirmed": success}
        return {"id": eid, "status": "completed", "success": success}

    def list_experiments(self) -> list[dict]:
        return [{"id": e["id"], "name": e["name"], "target": e["target"],
                 "fault_type": e["fault_type"], "status": e["status"],
                 "blast_radius_pct": e["blast_radius_pct"]}
                for e in self._experiments.values()]
