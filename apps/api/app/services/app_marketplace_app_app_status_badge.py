"""Status badge — shields.io-style status badge generator."""

import html
from urllib.parse import quote

COLORS = {"passing": "brightgreen", "failing": "red", "pending": "yellow",
           "unknown": "lightgrey", "active": "blue", "inactive": "grey"}


def generate_badge(*, label: str, value: str, status: str = "active",
                     style: str = "flat") -> dict:
    color = COLORS.get(status, "lightgrey")
    encoded_label = quote(label)
    encoded_value = quote(value)
    svg_url = f"https://img.shields.io/badge/{encoded_label}-{encoded_value}-{color}?style={style}"
    markdown = f"![{html.escape(label)}]({svg_url})"
    html_img = f'<img src="{html.escape(svg_url)}" alt="{html.escape(label)}" />'
    return {"svg_url": svg_url, "markdown": markdown, "html": html_img,
            "label": label, "value": value, "color": color, "style": style}


def build_badge_set(*, badges: list[dict]) -> dict:
    items = [generate_badge(**b) for b in badges]
    combined_md = " ".join(b["markdown"] for b in items)
    return {"badges": items, "total": len(items), "combined_markdown": combined_md}
