"""Fleet Vault — track HashiCorp Vault secret engine health."""
from __future__ import annotations
def fleet_vault_status(engines: list[dict]) -> dict:
    sealed = [e for e in engines if e.get("sealed", False)]
    total_secrets = sum(e.get("secret_count", 0) for e in engines)
    return {"engines": len(engines), "sealed": len(sealed), "total_secrets": total_secrets,
            "healthy": len(sealed) == 0}
