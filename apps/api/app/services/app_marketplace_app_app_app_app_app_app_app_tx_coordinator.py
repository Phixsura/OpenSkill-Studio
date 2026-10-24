"""Cross-service transaction coordinator — manage distributed transactions."""
from __future__ import annotations
import secrets
import time


def begin_transaction(participants: list[str]) -> dict:
    tx_id = f"tx_{secrets.token_urlsafe(12)}"
    return {"tx_id": tx_id, "participants": participants,
            "status": "preparing", "votes": {}, "started_at": time.time()}


def vote(tx: dict, participant: str, commit: bool) -> dict:
    tx["votes"][participant] = commit
    if len(tx["votes"]) == len(tx["participants"]):
        all_commit = all(tx["votes"].values())
        tx["status"] = "committed" if all_commit else "aborted"
    return {"participant": participant, "vote": "commit" if commit else "abort",
            "tx_status": tx["status"], "votes_received": len(tx["votes"]),
            "votes_needed": len(tx["participants"])}


def tx_summary(transactions: list[dict]) -> dict:
    committed = sum(1 for t in transactions if t["status"] == "committed")
    aborted = sum(1 for t in transactions if t["status"] == "aborted")
    preparing = sum(1 for t in transactions if t["status"] == "preparing")
    return {"total": len(transactions), "committed": committed,
            "aborted": aborted, "preparing": preparing,
            "success_rate": round(committed / max(len(transactions), 1) * 100)}
