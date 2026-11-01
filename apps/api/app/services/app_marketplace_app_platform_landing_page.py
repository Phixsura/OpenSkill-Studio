"""Platform landing page — the top-level marketing page for the platform."""


def build_landing_page(*, stats: dict, testimonials: list[dict],
                         features: list[dict]) -> dict:
    return {
        "hero": {
            "headline": "Build, Ship, and Scale Apps",
            "subheadline": "The complete developer platform for the modern web",
            "cta_primary": "Get Started Free",
            "cta_secondary": "View Documentation",
            "stats_bar": [
                {"label": "Apps", "value": f"{stats.get('apps', 0):,}+"},
                {"label": "Developers", "value": f"{stats.get('developers', 0):,}+"},
                {"label": "API Calls/Day", "value": f"{stats.get('api_calls_daily', 0) // 1000}K+"},
            ],
        },
        "features": [{"title": f["title"], "description": f["description"],
                       "icon": f.get("icon", "⚡")} for f in features[:6]],
        "testimonials": [{"quote": t["quote"], "author": t["author"],
                           "role": t.get("role", "")} for t in testimonials[:3]],
        "footer_links": [
            {"section": "Product", "links": ["Marketplace", "SDKs", "API", "Pricing"]},
            {"section": "Developers", "links": ["Docs", "API Reference", "Community", "Blog"]},
            {"section": "Company", "links": ["About", "Careers", "Contact", "Legal"]},
        ],
    }
