"""Deployment approval chain — multi-level approval workflow."""
from __future__ import annotations


class ApprovalChain:
    def __init__(self):
        self._chains: dict[str, dict] = {}

    def create(self, deploy_id: str, levels: list[dict]) -> dict:
        self._chains[deploy_id] = {
            "levels": [{"approver": l["approver"], "role": l.get("role", "reviewer"),
                        "approved": False} for l in levels],
            "current_level": 0, "status": "pending"}
        return {"deploy_id": deploy_id, "total_levels": len(levels)}

    def approve(self, deploy_id: str, approver: str) -> dict:
        chain = self._chains[deploy_id]
        level = chain["levels"][chain["current_level"]]
        if level["approver"] != approver:
            return {"approved": False, "reason": "wrong_approver"}
        level["approved"] = True
        chain["current_level"] += 1
        if chain["current_level"] >= len(chain["levels"]):
            chain["status"] = "fully_approved"
        return {"approved": True, "status": chain["status"],
                "remaining": len(chain["levels"]) - chain["current_level"]}

    def status(self, deploy_id: str) -> dict:
        chain = self._chains.get(deploy_id, {})
        return {"deploy_id": deploy_id, "status": chain.get("status", "not_found"),
                "levels": chain.get("levels", []),
                "current_level": chain.get("current_level", 0)}
