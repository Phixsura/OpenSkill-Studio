"""App API Developer Portal Theme — customizable developer portal branding."""
from __future__ import annotations
from dataclasses import dataclass
import re
import structlog

log = structlog.get_logger()

_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

@dataclass
class PortalTheme:
    primary_color: str
    secondary_color: str
    logo_url: str = ""
    favicon_url: str = ""
    font_family: str = "Inter"
    dark_mode: bool = True
    custom_css: str = ""
    portal_title: str = "Developer Portal"

class AppAPIDeveloperAPIApiDeveloperPortalTheme:
    def __init__(self) -> None:
        self._themes: dict[str, PortalTheme] = {}

    def set_theme(self, installation_id: str, primary_color: str, secondary_color: str, logo_url: str = "", favicon_url: str = "", font_family: str = "Inter", dark_mode: bool = True, custom_css: str = "", portal_title: str = "Developer Portal") -> PortalTheme:
        if not installation_id: raise ValueError("installation_id is required")
        if not _HEX_RE.match(primary_color): raise ValueError("primary_color must be hex (#RRGGBB)")
        if not _HEX_RE.match(secondary_color): raise ValueError("secondary_color must be hex")
        for url in (logo_url, favicon_url):
            if url and not url.startswith("https://"): raise ValueError("URLs must use HTTPS")
        if len(custom_css) > 10000: raise ValueError("custom_css too large (max 10KB)")
        t = PortalTheme(primary_color=primary_color, secondary_color=secondary_color, logo_url=logo_url, favicon_url=favicon_url, font_family=font_family, dark_mode=dark_mode, custom_css=custom_css, portal_title=portal_title)
        self._themes[installation_id] = t
        return t

    def get_theme(self, installation_id: str) -> PortalTheme:
        t = self._themes.get(installation_id)
        if t is None: return PortalTheme(primary_color="#3B82F6", secondary_color="#10B981")
        return t

    def has_custom_theme(self, installation_id: str) -> bool:
        return installation_id in self._themes
