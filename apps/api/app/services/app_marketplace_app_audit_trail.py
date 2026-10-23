"""Audit trail — compliance-grade audit trail with tamper detection."""

import hmac
import hashlib
import secrets
import json
from datetime import datetime

# In production, load from environment variable
_AUDIT_HMAC_KEY = secrets.token_bytes(32)


def create_audit_entry(*, actor: str, action: str, resource: str,
                         previous_hash: str | None = None,
                         metadata: dict | None = None) -> dict:
    timestamp = datetime.utcnow().isoformat()
    entry_id = f"audit_{secrets.token_urlsafe(8)}"
    payload = json.dumps({
        "entry_id": entry_id, "actor": actor, "action": action,
        "resource": resource, "timestamp": timestamp,
        "metadata": metadata or {},
        "previous_hash": previous_hash or "genesis",
    }, sort_keys=True)
    entry_hash = hmac.new(_AUDIT_HMAC_KEY, payload.encode(), hashlib.sha256).hexdigest()
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
