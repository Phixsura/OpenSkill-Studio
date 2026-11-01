"""Fleet AI Vault Integration — track secret management vault connections."""
from __future__ import annotations
def fleet_ai_vault_integration(vaults: list[dict]) -> dict:
    active = [v for v in vaults if v.get("active", True)]
    secrets = sum(v.get("secrets", 0) for v in vaults)
    accesses_24h = sum(v.get("accesses_24h", 0) for v in vaults)
    rotations = sum(v.get("rotations", 0) for v in vaults)
    return {"vaults": len(vaults), "active": len(active), "secrets": secrets,
            "accesses_24h": accesses_24h, "rotations": rotations, "sealed": len(active) == len(vaults)}
