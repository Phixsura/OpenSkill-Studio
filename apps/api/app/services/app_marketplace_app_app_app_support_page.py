"""App support page — developer support resources hub."""

import html

RESOURCES = [
    {"id": "docs", "title": "Documentation", "icon": "📖", "href": "/docs",
     "description": "Comprehensive guides and API reference"},
    {"id": "community", "title": "Community Forum", "icon": "💬", "href": "/community",
     "description": "Ask questions and share knowledge"},
    {"id": "status", "title": "Status Page", "icon": "🟢", "href": "/status",
     "description": "Real-time service status and incidents"},
    {"id": "changelog", "title": "Changelog", "icon": "📝", "href": "/changelog",
     "description": "Latest updates and release notes"},
    {"id": "support", "title": "Contact Support", "icon": "🎫", "href": "/support/contact",
     "description": "Get help from our support team"},
    {"id": "faq", "title": "FAQ", "icon": "❓", "href": "/faq",
     "description": "Frequently asked questions"},
]


def build_support_page(*, open_tickets: int = 0, recent_incidents: int = 0) -> dict:
    return {
        "resources": RESOURCES,
        "resource_count": len(RESOURCES),
        "open_tickets": open_tickets,
        "recent_incidents": recent_incidents,
        "has_alerts": open_tickets > 0 or recent_incidents > 0,
    }
