"""Change request — formal change management for production apps."""

import secrets
from datetime import datetime


RISK_LEVELS = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def create_change_request(*, title: str, description: str, risk: str,
                            requester: str, approvers: list[str]) -> dict:
    if risk not in RISK_LEVELS:
        return {"error": f"Invalid risk. Valid: {', '.join(sorted(RISK_LEVELS))}"}
    if not approvers:
        return {"error": "At least one approver required"}
    min_approvals = 1 if risk in ("low", "medium") else 2
    return {
        "cr_id": f"CR-{secrets.token_hex(4).upper()}",
        "title": title,
        "description": description,
        "risk": risk,
        "requester": requester,
        "approvers": approvers,
        "min_approvals": min_approvals,
        "current_approvals": 0,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
    }


def approve_change(*, cr: dict, approver: str) -> dict:
    if approver not in cr.get("approvers", []):
        return {"error": "Not an authorized approver"}
    new_count = cr.get("current_approvals", 0) + 1
    approved = new_count >= cr.get("min_approvals", 1)
    return {
        "cr_id": cr["cr_id"],
        "approved_by": approver,
        "current_approvals": new_count,
        "fully_approved": approved,
        "status": "approved" if approved else "pending",
    }
