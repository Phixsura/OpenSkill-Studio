"""App API Changelog Embed — embeddable changelog widget config."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class EmbedConfig:
    config_id: str
    theme: str = "light"
    max_entries: int = 5
    show_reactions: bool = True
    custom_css: str = ""

class AppAPIChangelogEmbed:
    def __init__(self) -> None:
        self._configs: dict[str, EmbedConfig] = {}

    def configure(self, installation_id: str, theme: str = "light", max_entries: int = 5, show_reactions: bool = True) -> EmbedConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if theme not in ("light", "dark", "auto"): raise ValueError("theme must be light, dark, or auto")
        config = EmbedConfig(config_id=installation_id, theme=theme, max_entries=max_entries, show_reactions=show_reactions)
        self._configs[installation_id] = config
        return config

    def get_config(self, installation_id: str) -> EmbedConfig:
        return self._configs.get(installation_id, EmbedConfig(config_id=installation_id))
