"""Status badge — generate embeddable status badges for apps."""

from xml.sax.saxutils import escape


BADGE_COLORS = {
    "operational": "#22c55e",
    "degraded": "#eab308",
    "outage": "#ef4444",
    "maintenance": "#3b82f6",
    "unknown": "#6b7280",
}


def generate_badge_svg(*, label: str, status: str, style: str = "flat") -> dict:
    color = BADGE_COLORS.get(status, BADGE_COLORS["unknown"])
    safe_label = escape(label)
    safe_status = escape(status)
    w_label = len(label) * 7 + 10
    w_status = len(status) * 7 + 10
    total_w = w_label + w_status
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="20">'
        f'<rect width="{w_label}" height="20" fill="#555"/>'
        f'<rect x="{w_label}" width="{w_status}" height="20" fill="{color}"/>'
        f'<text x="{w_label // 2}" y="14" fill="#fff" text-anchor="middle" font-size="11">{safe_label}</text>'
        f'<text x="{w_label + w_status // 2}" y="14" fill="#fff" text-anchor="middle" font-size="11">{safe_status}</text>'
        f'</svg>'
    )
    return {
        "svg": svg,
        "content_type": "image/svg+xml",
        "url": f"https://badge.openskill.dev/{escape(label)}/{escape(status)}.svg",
        "markdown": f"![{safe_label}]({f'https://badge.openskill.dev/{escape(label)}/{escape(status)}.svg'})",
    }
