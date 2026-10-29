"""API Developer Portal Config — configure developer portal appearance and content."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

@dataclass
class PortalConfig:
    portal_id: str
    title: str
    description: str = ""
    logo_url: str = ""
    primary_color: str = "#3B82F6"
    custom_domain: str = ""
    sections: list[str] = field(default_factory=lambda: ["docs", "api-reference", "changelog", "support"])
    analytics_enabled: bool = True
    signup_enabled: bool = True

_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
_DOMAIN_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9\-.]+\.[a-zA-Z]{2,}$")
VALID_SECTIONS = {"docs", "api-reference", "changelog", "support", "sdks", "tutorials", "status", "community"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiDeveloperPortalConfig:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], PortalConfig] = {}

    def create(self, installation_id: str, config: PortalConfig) -> PortalConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if not config.title: raise ValueError("title is required")
        if config.primary_color and not _COLOR_RE.match(config.primary_color):
            raise ValueError(f"Invalid color: {config.primary_color}")
        if config.custom_domain and not _DOMAIN_RE.match(config.custom_domain):
            raise ValueError(f"Invalid domain: {config.custom_domain}")
        invalid_sections = set(config.sections) - VALID_SECTIONS
        if invalid_sections: raise ValueError(f"Invalid sections: {invalid_sections}")
        key = (installation_id, config.portal_id)
        self._configs[key] = config
        return config

    def update(self, installation_id: str, portal_id: str, **kwargs: object) -> PortalConfig:
        config = self._get(installation_id, portal_id)
        for k, v in kwargs.items():
            if not hasattr(config, k): raise ValueError(f"Unknown field: {k}")
            if k == "primary_color" and v and not _COLOR_RE.match(str(v)):
                raise ValueError(f"Invalid color: {v}")
            setattr(config, k, v)
        return config

    def get(self, installation_id: str, portal_id: str) -> PortalConfig:
        return self._get(installation_id, portal_id)

    def list_portals(self, installation_id: str) -> list[PortalConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]

    def _get(self, installation_id: str, portal_id: str) -> PortalConfig:
        c = self._configs.get((installation_id, portal_id))
        if c is None: raise KeyError(f"Portal {portal_id} not found")
        return c
