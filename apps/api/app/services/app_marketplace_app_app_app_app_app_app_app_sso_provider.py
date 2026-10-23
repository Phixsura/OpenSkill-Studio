"""SSO provider manager — configure and validate SSO identity providers."""
from __future__ import annotations
from urllib.parse import urlparse
import html


class SsoProviderManager:
    def __init__(self):
        self._providers: dict[str, dict] = {}

    def add_provider(self, *, provider_id: str, name: str, protocol: str,
                      metadata_url: str, domains: list[str]) -> dict:
        parsed = urlparse(metadata_url)
        if parsed.scheme not in ("https",):
            return {"error": "metadata_url must use HTTPS"}
        safe_name = html.escape(name)
        self._providers[provider_id] = {
            "id": provider_id, "name": safe_name, "protocol": protocol,
            "metadata_url": metadata_url, "domains": domains,
            "enabled": True, "verified": False,
        }
        return {"provider_id": provider_id, "name": safe_name, "status": "configured"}

    def verify(self, provider_id: str) -> dict:
        p = self._providers.get(provider_id)
        if not p:
            return {"error": "Provider not found"}
        p["verified"] = True
        return {"provider_id": provider_id, "verified": True}

    def resolve_provider(self, email: str) -> dict:
        domain = email.split("@")[-1].lower() if "@" in email else ""
        for p in self._providers.values():
            if p["enabled"] and domain in p["domains"]:
                return {"found": True, "provider_id": p["id"], "name": p["name"],
                        "protocol": p["protocol"]}
        return {"found": False, "domain": domain}

    def list_providers(self) -> list[dict]:
        return [{"id": p["id"], "name": p["name"], "protocol": p["protocol"],
                 "domains": p["domains"], "enabled": p["enabled"], "verified": p["verified"]}
                for p in self._providers.values()]
