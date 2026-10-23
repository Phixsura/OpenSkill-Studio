"""Deployment approval workflow — require approvals before deploy."""
from __future__ import annotations
import time


def create_approval_request(deploy_id: str, requester: str, environment: str,
                             required_approvers: list[str]) -> dict:
    return {"deploy_id": deploy_id, "requester": requester, "environment": environment,
            "required_approvers": required_approvers, "approvals": [],
            "rejections": [], "status": "pending", "created_at": time.time()}


def approve(request: dict, approver: str) -> dict:
    if approver == request["requester"]:
        return {"approved": False, "error": "cannot_self_approve"}
    if approver in [a["approver"] for a in request["approvals"]]:
        return {"approved": False, "error": "already_approved"}
    request["approvals"].append({"approver": approver, "at": time.time()})
    approved_by = {a["approver"] for a in request["approvals"]}
    all_approved = all(r in approved_by for r in request["required_approvers"])
    if all_approved:
        request["status"] = "approved"
    return {"approved": True, "total_approvals": len(request["approvals"]),
            "all_approved": all_approved, "status": request["status"]}


def reject(request: dict, rejector: str, reason: str = "") -> dict:
    request["rejections"].append({"rejector": rejector, "reason": reason, "at": time.time()})
    request["status"] = "rejected"
    return {"rejected": True, "status": "rejected"}
