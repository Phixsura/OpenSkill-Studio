"""API Consumer SSO Config — configure Single Sign-On for consumer organizations."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

@dataclass
class SsoConfig:
    config_id: str
    consumer_id: str
    provider: str  # "saml", "oidc", "oauth2"
    issuer_url: str = ""
    client_id: str = ""
    domains: list[str] = field(default_factory=list)
    enabled: bool = False
    enforce: bool = False  # require SSO for all org members
    auto_provision: bool = True

VALID_PROVIDERS = {"saml", "oidc", "oauth2"}
_DOMAIN_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9\-.]+\.[a-zA-Z]{2,}$")

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerSsoConfig:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], SsoConfig] = {}

    def configure(self, installation_id: str, config: SsoConfig) -> SsoConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if config.provider not in VALID_PROVIDERS: raise ValueError(f"Invalid provider: {config.provider}")
        for d in config.domains:
            if not _DOMAIN_RE.match(d): raise ValueError(f"Invalid domain: {d}")
        if config.enforce and not config.enabled: raise ValueError("Cannot enforce disabled SSO")
        key = (installation_id, config.consumer_id)
        self._configs[key] = config
        return config

    def check_domain(self, installation_id: str, email: str) -> SsoConfig | None:
        domain = email.split("@")[-1].lower() if "@" in email else ""
        for (inst, _), cfg in self._configs.items():
            if inst == installation_id and cfg.enabled and domain in [d.lower() for d in cfg.domains]:
                return cfg
        return None

    def toggle(self, installation_id: str, consumer_id: str, enabled: bool) -> SsoConfig:
        cfg = self._get(installation_id, consumer_id)
        if not enabled and cfg.enforce: raise ValueError("Cannot disable enforced SSO without removing enforcement first")
        cfg.enabled = enabled
        return cfg

    def list_configs(self, installation_id: str) -> list[SsoConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]

    def _get(self, installation_id: str, consumer_id: str) -> SsoConfig:
        c = self._configs.get((installation_id, consumer_id))
        if c is None: raise KeyError(f"SSO config for {consumer_id} not found")
        return c
