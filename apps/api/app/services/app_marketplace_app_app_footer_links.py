"""Footer links — structured footer content with link sections."""

import html

DEFAULT_SECTIONS = {
    "Product": [
        {"label": "Features", "href": "/features"},
        {"label": "Pricing", "href": "/pricing"},
        {"label": "Marketplace", "href": "/marketplace"},
        {"label": "SDK", "href": "/sdk"},
    ],
    "Developers": [
        {"label": "Documentation", "href": "/docs"},
        {"label": "API Reference", "href": "/api"},
        {"label": "Changelog", "href": "/changelog"},
        {"label": "Status", "href": "/status"},
    ],
    "Company": [
        {"label": "About", "href": "/about"},
        {"label": "Blog", "href": "/blog"},
        {"label": "Careers", "href": "/careers"},
        {"label": "Contact", "href": "/contact"},
    ],
    "Legal": [
        {"label": "Privacy", "href": "/privacy"},
        {"label": "Terms", "href": "/terms"},
        {"label": "Cookie Policy", "href": "/cookies"},
    ],
}


def build_footer(*, sections: dict | None = None, copyright_year: int = 2026,
                   company: str = "OpenSkill") -> dict:
    sec = sections or DEFAULT_SECTIONS
    safe = {}
    total_links = 0
    for name, links in sec.items():
        safe[name] = [{"label": html.escape(l["label"]), "href": l["href"]} for l in links]
        total_links += len(links)
    return {"sections": safe, "section_count": len(safe), "total_links": total_links,
            "copyright": f"© {copyright_year} {html.escape(company)}. All rights reserved."}
