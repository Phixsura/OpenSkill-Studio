"""Embed code — generate embeddable widget snippets."""

import html
from urllib.parse import urlparse


def generate_embed(*, app_id: str, base_url: str, width: int = 400,
                    height: int = 300, theme: str = "light") -> dict:
    parsed = urlparse(base_url)
    if parsed.scheme not in ("https", "http"):
        return {"error": "Invalid base URL scheme"}
    widget_url = f"{base_url}/embed/{app_id}?theme={theme}"
    iframe = f'<iframe src="{html.escape(widget_url)}" width="{width}" height="{height}" frameborder="0" style="border:none;border-radius:8px;" loading="lazy"></iframe>'
    script = f'<script src="{html.escape(base_url)}/sdk/widget.js" data-app-id="{html.escape(app_id)}" data-theme="{theme}"></script>'
    return {"iframe": iframe, "script": script, "widget_url": widget_url,
            "width": width, "height": height, "theme": theme}
