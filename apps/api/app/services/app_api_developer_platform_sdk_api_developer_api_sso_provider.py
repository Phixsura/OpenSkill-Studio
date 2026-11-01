"""App API Developer SSO Provider — manage Single Sign-On provider configurations."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class SSOProviderConfig:
    provider_id: str
    provider_type: str  # "saml", "oidc", "oauth2"
    issuer_url: str
    client_id: str
    enabled: bool = True
    login_count: int = 0
    last_login_at: float = 0.0

class AppAPIDeveloperPlatformSDKApiDeveloperApiSSOProvider:
    def __init__(self) -> None:
        self._providers: dict[tuple[str, str], SSOProviderConfig] = {}

    def configure(self, installation_id: str, provider_id: str, provider_type: str, issuer_url: str, client_id: str) -> SSOProviderConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if provider_type not in ("saml", "oidc", "oauth2"): raise ValueError("invalid provider_type")
        if not issuer_url.startswith("https://"): raise ValueError("issuer_url must use HTTPS")
        key = (installation_id, provider_id)
        if key in self._providers: raise ValueError(f"Provider {provider_id} exists")
        p = SSOProviderConfig(provider_id=provider_id, provider_type=provider_type, issuer_url=issuer_url, client_id=client_id)
        self._providers[key] = p
        return p

    def record_login(self, installation_id: str, provider_id: str) -> SSOProviderConfig:
        key = (installation_id, provider_id)
        p = self._providers.get(key)
        if p is None: raise KeyError(f"Provider {provider_id} not found")
        if not p.enabled: raise ValueError("Provider is disabled")
        p.login_count += 1
        import time; p.last_login_at = time.time()
        return p

    def toggle(self, installation_id: str, provider_id: str, enabled: bool) -> SSOProviderConfig:
        key = (installation_id, provider_id)
        p = self._providers.get(key)
        if p is None: raise KeyError(f"Provider {provider_id} not found")
        p.enabled = enabled
        return p

    def active_providers(self, installation_id: str) -> list[SSOProviderConfig]:
        return [p for (inst, _), p in self._providers.items() if inst == installation_id and p.enabled]

    def all_providers(self, installation_id: str) -> list[SSOProviderConfig]:
        return [p for (inst, _), p in self._providers.items() if inst == installation_id]
