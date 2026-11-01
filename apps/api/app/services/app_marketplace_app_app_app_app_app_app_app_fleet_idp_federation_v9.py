"""Fleet IdP Federation v9 — track identity provider SSO connections."""
from __future__ import annotations
def fleet_idp_federation_v9(providers: list[dict]) -> dict:
    connected = [p for p in providers if p.get("connected")]
    saml = [p for p in providers if p.get("protocol") == "SAML"]
    oidc = [p for p in providers if p.get("protocol") == "OIDC"]
    return {"total": len(providers), "connected": len(connected), "saml": len(saml),
            "oidc": len(oidc), "healthy": len(connected) == len(providers)}
