"""Developer agreement — track acceptance of developer terms and agreements."""
from __future__ import annotations
import time


AGREEMENTS = {
    "developer_tos": {"title": "Developer Terms of Service", "version": "2.0", "required": True},
    "marketplace_guidelines": {"title": "Marketplace Guidelines", "version": "1.5", "required": True},
    "data_processing": {"title": "Data Processing Agreement", "version": "1.0", "required": True},
    "branding_guidelines": {"title": "Branding Guidelines", "version": "1.0", "required": False},
}


def check_agreements(accepted: dict[str, str]) -> dict:
    results = []
    missing_required = []
    for aid, info in AGREEMENTS.items():
        accepted_version = accepted.get(aid, "")
        current = accepted_version == info["version"]
        outdated = bool(accepted_version) and not current
        results.append({"id": aid, "title": info["title"], "version": info["version"],
                         "required": info["required"], "accepted": current,
                         "outdated": outdated})
        if info["required"] and not current:
            missing_required.append(info["title"])
    return {"results": results, "all_accepted": len(missing_required) == 0,
            "missing_required": missing_required, "total": len(results)}


def accept_agreement(agreement_id: str) -> dict:
    info = AGREEMENTS.get(agreement_id)
    if not info:
        return {"error": "Unknown agreement"}
    return {"accepted": agreement_id, "version": info["version"],
            "timestamp": time.time()}
