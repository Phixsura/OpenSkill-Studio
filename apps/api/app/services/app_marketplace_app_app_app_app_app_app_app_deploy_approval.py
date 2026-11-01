"""Deployment approval workflow — multi-stage approval for deployments."""
from __future__ import annotations


class DeploymentApproval:
    def __init__(self, required_approvers: int = 2):
        self._required = required_approvers
        self._deployments: dict[str, dict] = {}

    def create(self, deploy_id: str, version: str, env: str) -> dict:
        self._deployments[deploy_id] = {
            "version": version, "env": env, "approvals": [],
            "rejections": [], "status": "pending"}
        return {"deploy_id": deploy_id, "status": "pending", "required": self._required}

    def approve(self, deploy_id: str, approver: str) -> dict:
        d = self._deployments[deploy_id]
        if approver not in d["approvals"]:
            d["approvals"].append(approver)
        if len(d["approvals"]) >= self._required:
            d["status"] = "approved"
        return {"deploy_id": deploy_id, "status": d["status"],
                "approvals": len(d["approvals"]), "needed": max(0, self._required - len(d["approvals"]))}

    def reject(self, deploy_id: str, rejector: str, reason: str) -> dict:
        d = self._deployments[deploy_id]
        d["rejections"].append({"by": rejector, "reason": reason})
        d["status"] = "rejected"
        return {"deploy_id": deploy_id, "status": "rejected", "reason": reason}

    def get(self, deploy_id: str) -> dict:
        d = self._deployments[deploy_id]
        return {"deploy_id": deploy_id, **d}
