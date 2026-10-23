"""Deployment approval gate — require approvals before production deploys."""
from __future__ import annotations
import time


class DeploymentGate:
    def __init__(self, *, required_approvals: int = 2):
        self._gates: dict[str, dict] = {}
        self._required = required_approvals

    def create_gate(self, deploy_id: str, *, version: str, env: str,
                     requester: str) -> dict:
        self._gates[deploy_id] = {
            "id": deploy_id, "version": version, "env": env,
            "requester": requester, "approvals": [],
            "rejections": [], "status": "pending",
            "created_at": time.time(),
        }
        return {"id": deploy_id, "status": "pending", "required": self._required}

    def approve(self, deploy_id: str, *, approver: str, comment: str = "") -> dict:
        gate = self._gates.get(deploy_id)
        if not gate:
            return {"error": "Gate not found"}
        if approver == gate["requester"]:
            return {"error": "Cannot self-approve"}
        if approver in [a["approver"] for a in gate["approvals"]]:
            return {"error": "Already approved"}
        gate["approvals"].append({"approver": approver, "comment": comment})
        if len(gate["approvals"]) >= self._required:
            gate["status"] = "approved"
        return {"id": deploy_id, "status": gate["status"],
                "approvals": len(gate["approvals"]), "required": self._required}

    def reject(self, deploy_id: str, *, reviewer: str, reason: str) -> dict:
        gate = self._gates.get(deploy_id)
        if not gate:
            return {"error": "Gate not found"}
        gate["rejections"].append({"reviewer": reviewer, "reason": reason})
        gate["status"] = "rejected"
        return {"id": deploy_id, "status": "rejected", "reason": reason}

    def can_deploy(self, deploy_id: str) -> dict:
        gate = self._gates.get(deploy_id)
        if not gate:
            return {"allowed": False, "reason": "gate_not_found"}
        return {"allowed": gate["status"] == "approved",
                "status": gate["status"],
                "approvals": len(gate["approvals"]),
                "required": self._required}
