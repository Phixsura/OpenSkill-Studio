"""Platform footer links — manage navigational footer with grouped links."""
from __future__ import annotations


def build_footer(sections: list[dict] | None = None) -> dict:
    default_sections = [
        {"title": "Product", "links": [
            {"label": "Features", "url": "/features"}, {"label": "Pricing", "url": "/pricing"},
            {"label": "Changelog", "url": "/changelog"}, {"label": "Roadmap", "url": "/roadmap"}]},
        {"title": "Developers", "links": [
            {"label": "Documentation", "url": "/docs"}, {"label": "API Reference", "url": "/api"},
            {"label": "SDKs", "url": "/sdks"}, {"label": "Status", "url": "/status"}]},
        {"title": "Company", "links": [
            {"label": "About", "url": "/about"}, {"label": "Blog", "url": "/blog"},
            {"label": "Careers", "url": "/careers"}, {"label": "Contact", "url": "/contact"}]},
        {"title": "Legal", "links": [
            {"label": "Privacy", "url": "/privacy"}, {"label": "Terms", "url": "/terms"},
            {"label": "Security", "url": "/security"}, {"label": "DPA", "url": "/dpa"}]},
    ]
    secs = sections or default_sections
    total_links = sum(len(s["links"]) for s in secs)
    return {"sections": secs, "section_count": len(secs),
            "total_links": total_links, "copyright": "© 2026 OpenSkill"}
