"""Fleet Sealed Secrets — track encrypted secret management."""
from __future__ import annotations
def fleet_sealed_secrets(secrets: list[dict]) -> dict:
    sealed = [s for s in secrets if s.get("sealed", False)]
    unsealed = len(secrets) - len(sealed)
    expired_key = [s for s in secrets if s.get("key_expired", False)]
    return {"total": len(secrets), "sealed": len(sealed), "unsealed": unsealed,
            "expired_keys": len(expired_key), "secure": unsealed == 0 and len(expired_key) == 0}
