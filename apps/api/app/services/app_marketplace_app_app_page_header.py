"""Page header — generate page header metadata."""

import html


def build_page_header(*, title: str, subtitle: str | None = None,
                        breadcrumbs: list[dict] | None = None,
                        actions: list[dict] | None = None) -> dict:
    return {
        "title": html.escape(title),
        "subtitle": html.escape(subtitle) if subtitle else None,
        "breadcrumbs": breadcrumbs or [],
        "actions": actions or [],
        "has_breadcrumbs": bool(breadcrumbs),
        "has_actions": bool(actions),
    }
