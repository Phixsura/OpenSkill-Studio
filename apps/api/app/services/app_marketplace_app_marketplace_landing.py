"""Marketplace landing — the grand entry page combining everything."""


def build_landing_page(*, hero: dict, featured_apps: list[dict], categories: list[dict],
                         stats: dict, testimonials: list[dict], cta: dict) -> dict:
    return {
        "page_type": "marketplace_landing",
        "hero": {"title": hero.get("title", "OpenSkill Marketplace"),
                  "subtitle": hero.get("subtitle", "Discover apps to supercharge your workflow"),
                  "cta_label": hero.get("cta", "Explore Apps"), "cta_url": "/marketplace"},
        "sections": [
            {"key": "stats", "type": "stats_bar", "data": {
                "apps": stats.get("apps", 0), "developers": stats.get("developers", 0),
                "installs": stats.get("installs", 0)}},
            {"key": "featured", "type": "app_carousel", "title": "Featured Apps", "apps": featured_apps[:8]},
            {"key": "categories", "type": "category_grid", "title": "Browse by Category", "categories": categories},
            {"key": "testimonials", "type": "testimonial_carousel", "title": "What Developers Say",
             "testimonials": testimonials[:6]},
            {"key": "cta", "type": "cta_section", "title": cta.get("title", "Start Building"),
             "subtitle": cta.get("subtitle", "Join thousands of developers"), "button_label": cta.get("button", "Get Started"),
             "button_url": cta.get("url", "/developer/register")},
        ],
    }


def build_testimonial(*, author: str, role: str, company: str, quote: str, rating: int) -> dict:
    return {"author": author, "role": role, "company": company, "quote": quote,
            "rating": rating, "avatar_initial": author[0] if author else "?"}
