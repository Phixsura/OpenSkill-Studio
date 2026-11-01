"""App embed widget — generate embeddable widgets for external sites."""
from __future__ import annotations
import html


def generate_embed_code(*, app_id: str, app_name: str, style: str = "card",
                          theme: str = "light") -> dict:
    safe_name = html.escape(app_name)
    width = "300" if style == "card" else "200" if style == "badge" else "400"
    height = "200" if style == "card" else "40" if style == "badge" else "300"
    embed_url = f"https://marketplace.openskill.io/embed/{app_id}?style={style}&theme={theme}"
    iframe_code = f'<iframe src="{embed_url}" width="{width}" height="{height}" frameborder="0"></iframe>'
    return {
        "app_id": app_id, "app_name": safe_name, "style": style,
        "theme": theme, "embed_url": embed_url,
        "iframe_code": iframe_code, "width": width, "height": height,
    }


def list_embed_styles() -> list[dict]:
    return [
        {"id": "card", "label": "Card", "width": 300, "height": 200, "preview": "Full app card"},
        {"id": "badge", "label": "Badge", "width": 200, "height": 40, "preview": "Compact badge"},
        {"id": "full", "label": "Full", "width": 400, "height": 300, "preview": "Detailed view"},
    ]
