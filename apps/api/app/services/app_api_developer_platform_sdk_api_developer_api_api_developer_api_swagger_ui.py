"""App API Developer Swagger UI — manage interactive API documentation UI settings."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class SwaggerUIConfig:
    title: str
    version: str
    base_url: str
    auth_type: str = "api_key"  # "api_key", "oauth2", "bearer", "none"
    theme: str = "light"  # "light", "dark"
    try_it_enabled: bool = True
    endpoints_visible: int = 0
    page_views: int = 0

class AppAPIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiSwaggerUI:
    def __init__(self) -> None:
        self._configs: dict[str, SwaggerUIConfig] = {}

    def configure(self, installation_id: str, title: str, version: str, base_url: str, auth_type: str = "api_key", theme: str = "light", try_it_enabled: bool = True) -> SwaggerUIConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if auth_type not in ("api_key", "oauth2", "bearer", "none"): raise ValueError("invalid auth_type")
        if theme not in ("light", "dark"): raise ValueError("invalid theme")
        if not base_url.startswith("https://"): raise ValueError("base_url must use HTTPS")
        c = SwaggerUIConfig(title=title, version=version, base_url=base_url, auth_type=auth_type, theme=theme, try_it_enabled=try_it_enabled)
        self._configs[installation_id] = c
        return c

    def record_view(self, installation_id: str) -> SwaggerUIConfig:
        c = self._configs.get(installation_id)
        if c is None: raise KeyError("No Swagger UI configured")
        c.page_views += 1
        return c

    def get(self, installation_id: str) -> SwaggerUIConfig | None:
        return self._configs.get(installation_id)
