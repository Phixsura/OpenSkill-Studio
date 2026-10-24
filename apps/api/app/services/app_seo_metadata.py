"""SEO metadata — generate meta tags for marketplace pages."""


def build_app_seo(app: dict, *, base_url: str = "https://marketplace.openskill.studio") -> dict:
    name = app.get("name", "App")
    desc = app.get("description", f"{name} on OpenSkill Marketplace")[:160]
    slug = app.get("slug", "")
    return {
        "title": f"{name} | OpenSkill Marketplace",
        "description": desc,
        "canonical": f"{base_url}/apps/{slug}",
        "og": {"title": name, "description": desc, "type": "website", "url": f"{base_url}/apps/{slug}",
               "image": app.get("icon_url", f"{base_url}/default-icon.png")},
    }


def build_category_seo(category: str) -> dict:
    labels = {"connector": "Connectors", "automation": "Automation Apps", "analytics": "Analytics Tools"}
    label = labels.get(category, category.replace("_", " ").title())
    return {"title": f"{label} | OpenSkill Marketplace", "description": f"Browse {label.lower()} on OpenSkill Marketplace"}
