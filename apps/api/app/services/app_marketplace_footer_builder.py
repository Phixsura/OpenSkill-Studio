"""Marketplace footer builder — build footer data for marketplace pages."""

def build_marketplace_footer() -> dict:
    return {
        "sections": {
            "Browse": [{"label": "All Apps", "url": "/marketplace/apps"}, {"label": "Categories", "url": "/marketplace/categories"},
                       {"label": "Featured", "url": "/marketplace/featured"}, {"label": "Trending", "url": "/marketplace/trending"}],
            "Developers": [{"label": "Developer Portal", "url": "/dashboard/developer"}, {"label": "Documentation", "url": "/docs/developer"},
                           {"label": "API Reference", "url": "/docs/api"}, {"label": "SDKs", "url": "/docs/sdk"}],
            "Resources": [{"label": "Blog", "url": "/blog"}, {"label": "Community", "url": "/community"},
                          {"label": "Status", "url": "/status"}, {"label": "Support", "url": "/support"}],
        },
        "copyright": "© 2026 OpenSkill Studio",
    }
