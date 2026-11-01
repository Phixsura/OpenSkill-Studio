"""App SSO Provider — manage Single Sign-On provider configurations.

Manages SSO providers:
- Configure SAML/OIDC providers
- Enable/disable per provider
- Track authentication counts
- Per-installation scoped providers
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class SSOProvider:
    """An SSO provider configuration."""

    provider_id: str
    provider_type: str  # "saml", "oidc"
    name: str
    issuer_url: str
    client_id: str = ""
    enabled: bool = True
    auth_count: int = 0
    error_count: int = 0

    @property
    def success_rate(self) -> float:
        total = self.auth_count + self.error_count
        if total == 0:
            return 100.0
        return round(self.auth_count / total * 100, 1)


VALID_TYPES = {"saml", "oidc"}


class AppSSOProvider:
    """Manage Single Sign-On provider configurations."""

    def __init__(self) -> None:
        self._providers: dict[tuple[str, str], SSOProvider] = {}

    def configure(
        self, installation_id: str, provider_id: str, provider_type: str,
        name: str, issuer_url: str, client_id: str = "",
    ) -> SSOProvider:
        if not installation_id:
            raise ValueError("installation_id is required")
        if provider_type not in VALID_TYPES:
            raise ValueError(f"provider_type must be one of {VALID_TYPES}")
        if not issuer_url:
            raise ValueError("issuer_url is required")

        provider = SSOProvider(
            provider_id=provider_id, provider_type=provider_type,
            name=name, issuer_url=issuer_url, client_id=client_id,
        )
        self._providers[(installation_id, provider_id)] = provider
        return provider

    def record_auth(self, installation_id: str, provider_id: str, success: bool) -> SSOProvider:
        p = self._get(installation_id, provider_id)
        if success:
            p.auth_count += 1
        else:
            p.error_count += 1
        return p

    def toggle(self, installation_id: str, provider_id: str, enabled: bool) -> SSOProvider:
        p = self._get(installation_id, provider_id)
        p.enabled = enabled
        return p

    def enabled_providers(self, installation_id: str) -> list[SSOProvider]:
        return [p for (inst, _), p in self._providers.items() if inst == installation_id and p.enabled]

    def list_providers(self, installation_id: str) -> list[SSOProvider]:
        return [p for (inst, _), p in self._providers.items() if inst == installation_id]

    def _get(self, installation_id: str, provider_id: str) -> SSOProvider:
        key = (installation_id, provider_id)
        p = self._providers.get(key)
        if p is None:
            raise KeyError(f"Provider {provider_id} not found")
        return p
