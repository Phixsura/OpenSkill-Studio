"""Hero section — landing page hero content builder."""

import html
from urllib.parse import urlparse


def build_hero(*, title: str, subtitle: str, cta_primary: dict,
                 cta_secondary: dict | None = None, badge: str | None = None,
                 stats: list[dict] | None = None) -> dict:
    return {
        "title": html.escape(title),
        "subtitle": html.escape(subtitle),
        "badge": html.escape(badge) if badge else None,
        "cta_primary": {"label": html.escape(cta_primary.get("label", "")),
                         "href": cta_primary.get("href", "#")},
        "cta_secondary": {"label": html.escape(cta_secondary.get("label", "")),
                           "href": cta_secondary.get("href", "#")} if cta_secondary else None,
        "stats": [{"value": html.escape(str(s.get("value", ""))),
                    "label": html.escape(s.get("label", ""))} for s in (stats or [])],
    }
