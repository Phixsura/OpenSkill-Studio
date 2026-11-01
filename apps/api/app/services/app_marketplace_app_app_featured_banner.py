"""Featured banner — promotional banner for marketplace homepage."""

import html
from urllib.parse import urlparse


def build_featured_banner(*, title: str, subtitle: str, cta_label: str,
                             cta_href: str, background_color: str = "#3B82F6",
                             icon: str = "🎉") -> dict:
    parsed = urlparse(cta_href)
    safe_href = cta_href if parsed.scheme in ("https", "http", "") else "#"
    return {
        "title": html.escape(title),
        "subtitle": html.escape(subtitle),
        "cta_label": html.escape(cta_label),
        "cta_href": safe_href,
        "background_color": background_color,
        "icon": icon,
        "dismissible": True,
    }
