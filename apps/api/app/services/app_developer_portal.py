"""App Developer Portal — manage developer portal configuration.

Manages developer portal:
- Portal settings (name, logo, theme)
- Navigation sections
- Quick links
- Per-installation scoped portals
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class NavSection:
    """A navigation section."""

    section_id: str
    title: str
    items: list[dict] = field(default_factory=list)  # [{label, href}]
    sort_order: int = 0


@dataclass
class PortalConfig:
    """Developer portal configuration."""

    portal_name: str
    logo_url: str = ""
    theme_color: str = "#000000"
    welcome_message: str = ""
    sections: list[NavSection] = field(default_factory=list)


class AppDeveloperPortal:
    """Manage developer portal configuration."""

    def __init__(self) -> None:
        self._portals: dict[str, PortalConfig] = {}

    def configure(
        self, installation_id: str, portal_name: str,
        logo_url: str = "", theme_color: str = "#000000",
        welcome_message: str = "",
    ) -> PortalConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not portal_name:
            raise ValueError("portal_name is required")

        config = PortalConfig(
            portal_name=portal_name, logo_url=logo_url,
            theme_color=theme_color, welcome_message=welcome_message,
        )
        self._portals[installation_id] = config
        return config

    def add_section(
        self, installation_id: str, section_id: str, title: str,
        items: list[dict], sort_order: int = 0,
    ) -> NavSection:
        config = self._get(installation_id)
        section = NavSection(
            section_id=section_id, title=title,
            items=items, sort_order=sort_order,
        )
        config.sections.append(section)
        config.sections.sort(key=lambda s: s.sort_order)
        return section

    def get_portal(self, installation_id: str) -> PortalConfig:
        return self._get(installation_id)

    def update_theme(self, installation_id: str, theme_color: str) -> PortalConfig:
        config = self._get(installation_id)
        config.theme_color = theme_color
        return config

    def _get(self, installation_id: str) -> PortalConfig:
        config = self._portals.get(installation_id)
        if config is None:
            raise KeyError("Portal not configured")
        return config
