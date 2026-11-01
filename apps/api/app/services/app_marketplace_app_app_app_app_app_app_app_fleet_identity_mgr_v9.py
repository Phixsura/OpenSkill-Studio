"""Fleet Identity Manager v9 — track identity lifecycle and federation."""
from __future__ import annotations
def fleet_identity_mgr_v9(identities: list[dict]) -> dict:
    active = [i for i in identities if i.get("active")]
    federated = [i for i in identities if i.get("federated")]
    mfa_enabled = [i for i in identities if i.get("mfa")]
    return {"total": len(identities), "active": len(active), "federated": len(federated),
            "mfa_enabled": len(mfa_enabled), "healthy": len(mfa_enabled) == len(identities)}
