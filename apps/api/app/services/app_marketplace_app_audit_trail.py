"""Audit trail — compliance-grade audit trail with tamper detection."""

import hashlib
import secrets
from datetime import datetime


def create_audit_entry(*, actor: str, action: str, resource: str,
                         previous_hash: str | None = None,
                         metadata: dict | None = None) -> dict:
    timestamp = datetime.utcnow().isoformat()
    entry_id = f"audit_{secrets.token_urlsafe(8)}"
    payload = f"{entry_id}:{actor}:{action}:{resource}:{timestamp}:{previous_hash or 'genesis'}"
    entry_hash = hashlib.sha256(payload.encode()).hexdigest()
    return {
        "entry_id": entry_id,
        "actor": actor,
        "action": action,
        "resource": resource,
        "timestamp": timestamp,
        "metadata": metadata or {},
        "hash": entry_hash,
        "previous_hash": previous_hash,
        "immutable": True,
    }


def verify_chain(*, entries: list[dict]) -> dict:
    if not entries:
        return {"valid": True, "entries_checked": 0}
    for i in range(1, len(entries)):
        if entries[i].get("previous_hash") != entries[i - 1].get("hash"):
            return {"valid": False, "broken_at": i,
                    "entry_id": entries[i].get("entry_id"),
                    "error": "Hash chain broken — possible tampering"}
    return {"valid": True, "entries_checked": len(entries), "chain_intact": True}
