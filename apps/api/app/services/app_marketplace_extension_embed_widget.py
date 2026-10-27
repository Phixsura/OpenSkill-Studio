"""Extension Embed Widget — generate embeddable widgets for external sites."""
from __future__ import annotations
from dataclasses import dataclass
import html
import re

ALLOWED_THEMES = {"light", "dark", "auto"}
ALLOWED_SIZES = {"small", "medium", "large"}


@dataclass
class EmbedConfig:
    extension_id: str
    theme: str = "auto"
    size: str = "medium"
    show_rating: bool = True
    show_installs: bool = True
    show_button: bool = True

    def __post_init__(self):
        if self.theme not in ALLOWED_THEMES:
            raise ValueError(f"Invalid theme: {self.theme}")
        if self.size not in ALLOWED_SIZES:
            raise ValueError(f"Invalid size: {self.size}")


class ExtEmbedWidgetService:
    BASE_URL = "https://marketplace.openskill.dev"

    def generate_html(self, config: EmbedConfig, ext_name: str, rating: float = 0,
                      installs: int = 0) -> str:
        name = html.escape(ext_name)
        stars = "★" * round(rating) + "☆" * (5 - round(rating))
        parts = [f'<div class="osk-embed osk-{config.size} osk-{config.theme}">']
        parts.append(f'<span class="osk-name">{name}</span>')
        if config.show_rating:
            parts.append(f'<span class="osk-rating">{stars} {rating:.1f}</span>')
        if config.show_installs:
            parts.append(f'<span class="osk-installs">{installs:,} installs</span>')
        if config.show_button:
            url = html.escape(f"{self.BASE_URL}/ext/{config.extension_id}")
            parts.append(f'<a href="{url}" class="osk-btn">Install</a>')
        parts.append('</div>')
        return "\n".join(parts)

    def generate_iframe(self, config: EmbedConfig) -> str:
        eid = html.escape(config.extension_id)
        w = {"small": 200, "medium": 300, "large": 400}[config.size]
        h = {"small": 80, "medium": 120, "large": 160}[config.size]
        src = html.escape(f"{self.BASE_URL}/embed/{eid}?theme={config.theme}")
        return f'<iframe src="{src}" width="{w}" height="{h}" frameborder="0"></iframe>'

    def generate_markdown(self, config: EmbedConfig, ext_name: str,
                          rating: float = 0) -> str:
        name = ext_name.replace("[", "\\[").replace("]", "\\]")
        url = f"{self.BASE_URL}/ext/{config.extension_id}"
        stars = "★" * round(rating)
        return f"[**{name}**]({url}) {stars} ({rating:.1f}/5.0)"
