"""App embed widget — generate embeddable widgets for external sites."""

import html


def generate_embed_code(*, app_id: str, app_name: str, theme: str = "light",
                          width: int = 300, height: int = 200) -> dict:
    safe_name = html.escape(app_name)
    safe_id = html.escape(app_id)
    valid_themes = {"light", "dark", "auto"}
    if theme not in valid_themes:
        return {"error": f"Invalid theme. Valid: {', '.join(sorted(valid_themes))}"}
    iframe_url = f"https://marketplace.openskill.dev/embed/{safe_id}?theme={theme}"
    iframe = f'<iframe src="{iframe_url}" width="{width}" height="{height}" frameborder="0" title="{safe_name}"></iframe>'
    script_tag = f'<script src="https://marketplace.openskill.dev/widget.js" data-app="{safe_id}" data-theme="{theme}"></script>'
    return {
        "iframe_code": iframe,
        "script_code": script_tag,
        "preview_url": iframe_url,
        "dimensions": {"width": width, "height": height},
    }


def get_embed_analytics(*, embeds: list[dict]) -> dict:
    total_views = sum(e.get("views", 0) for e in embeds)
    total_clicks = sum(e.get("clicks", 0) for e in embeds)
    ctr = round(total_clicks / max(total_views, 1) * 100, 1)
    top_domains = {}
    for e in embeds:
        domain = e.get("domain", "unknown")
        top_domains[domain] = top_domains.get(domain, 0) + e.get("views", 0)
    sorted_domains = sorted(top_domains.items(), key=lambda x: x[1], reverse=True)[:5]
    return {"total_views": total_views, "total_clicks": total_clicks,
            "ctr": ctr, "top_domains": [{"domain": d, "views": v} for d, v in sorted_domains]}
