"""Complete navigation — the ultimate platform navigation structure."""

import html

MAIN_NAV = [
    {"id": "marketplace", "label": "Marketplace", "href": "/marketplace", "icon": "🏪"},
    {"id": "console", "label": "Console", "href": "/console", "icon": "💻"},
    {"id": "docs", "label": "Docs", "href": "/docs", "icon": "📖"},
    {"id": "community", "label": "Community", "href": "/community", "icon": "💬"},
    {"id": "status", "label": "Status", "href": "/status", "icon": "🟢"},
]

CONSOLE_NAV = [
    {"id": "dashboard", "label": "Dashboard", "href": "/console", "icon": "📊"},
    {"id": "apps", "label": "My Apps", "href": "/console/apps", "icon": "📦"},
    {"id": "analytics", "label": "Analytics", "href": "/console/analytics", "icon": "📈"},
    {"id": "webhooks", "label": "Webhooks", "href": "/console/webhooks", "icon": "🔗"},
    {"id": "keys", "label": "API Keys", "href": "/console/keys", "icon": "🔑"},
    {"id": "team", "label": "Team", "href": "/console/team", "icon": "👥"},
    {"id": "billing", "label": "Billing", "href": "/console/billing", "icon": "💳"},
    {"id": "settings", "label": "Settings", "href": "/console/settings", "icon": "⚙️"},
]

FOOTER_NAV = {
    "Product": [{"label": "Marketplace", "href": "/marketplace"}, {"label": "Pricing", "href": "/pricing"},
                {"label": "SDK", "href": "/sdk"}, {"label": "CLI", "href": "/cli"}],
    "Developers": [{"label": "Docs", "href": "/docs"}, {"label": "API Reference", "href": "/api"},
                    {"label": "Changelog", "href": "/changelog"}, {"label": "Status", "href": "/status"}],
    "Company": [{"label": "About", "href": "/about"}, {"label": "Blog", "href": "/blog"},
                {"label": "Contact", "href": "/contact"}],
    "Legal": [{"label": "Terms", "href": "/terms"}, {"label": "Privacy", "href": "/privacy"}],
}


def build_complete_nav(*, active_section: str = "", active_console: str = "") -> dict:
    main = [{"id": n["id"], "label": n["label"], "href": n["href"], "icon": n["icon"],
             "active": n["id"] == active_section} for n in MAIN_NAV]
    console = [{"id": n["id"], "label": n["label"], "href": n["href"], "icon": n["icon"],
                "active": n["id"] == active_console} for n in CONSOLE_NAV]
    return {"main_nav": main, "console_nav": console, "footer_nav": FOOTER_NAV,
            "main_count": len(main), "console_count": len(console)}
