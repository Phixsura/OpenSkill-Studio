"""App embed — generate embeddable widgets for external sites."""

import hashlib
import html


def generate_embed_code(*, app: dict, theme: str = "light", width: int = 300) -> dict:
    app_id = app["id"]
    name = html.escape(app.get("name", ""))
    slug = app.get("slug", "")
    base_url = "https://openskill.dev"
    iframe_src = f"{base_url}/embed/apps/{slug}?theme={theme}"
    iframe_html = f'<iframe src="{iframe_src}" width="{width}" height="200" frameborder="0" title="{name}"></iframe>'
    badge_html = f'<a href="{base_url}/marketplace/apps/{slug}"><img src="{base_url}/badge/{slug}.svg" alt="{name} on OpenSkill" /></a>'
    return {
        "app_id": app_id, "iframe": iframe_html, "badge": badge_html,
        "direct_link": f"{base_url}/marketplace/apps/{slug}",
    }


def generate_install_button(*, app: dict, style: str = "default") -> str:
    slug = app.get("slug", "")
    name = html.escape(app.get("name", ""))
    base = "https://openskill.dev"
    if style == "minimal":
        return f'<a href="{base}/install/{slug}">Install {name}</a>'
    return f'<a href="{base}/install/{slug}" style="display:inline-block;padding:8px 16px;background:#2563eb;color:#fff;border-radius:6px;text-decoration:none">Install {name}</a>'


def validate_embed_domain(*, domain: str, allowed_domains: list[str]) -> bool:
    return domain in allowed_domains or "*" in allowed_domains
