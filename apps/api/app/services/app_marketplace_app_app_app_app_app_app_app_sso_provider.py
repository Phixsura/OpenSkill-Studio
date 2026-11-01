"""SSO provider config — manage OAuth/SAML identity providers."""
from __future__ import annotations
from urllib.parse import urlparse

PROTOCOLS = {"oauth2", "saml", "oidc"}


def create_provider(name: str, protocol: str, client_id: str,
                    authorize_url: str, token_url: str = "") -> dict:
    if protocol not in PROTOCOLS:
        return {"created": False, "error": f"unsupported protocol, use {sorted(PROTOCOLS)}"}
    parsed = urlparse(authorize_url)
    if parsed.scheme not in ("https",):
        return {"created": False, "error": "authorize_url must use https"}
    return {"created": True, "name": name, "protocol": protocol,
            "client_id": client_id, "authorize_url": authorize_url,
            "token_url": token_url, "status": "active"}


def list_providers(providers: list[dict]) -> dict:
    active = sum(1 for p in providers if p.get("status") == "active")
    by_protocol: dict[str, int] = {}
    for p in providers:
        proto = p.get("protocol", "unknown")
        by_protocol[proto] = by_protocol.get(proto, 0) + 1
    return {"providers": providers, "total": len(providers),
            "active": active, "by_protocol": by_protocol}
