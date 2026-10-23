"""About page — platform information, team, and mission."""


def build_about_page(*, stats: dict, team: list[dict], milestones: list[dict]) -> dict:
    return {
        "page_type": "about",
        "hero": {
            "title": "Building the Future of App Development",
            "subtitle": "OpenSkill empowers developers to build, share, and grow their apps with a complete platform.",
        },
        "stats": [
            {"label": "Apps Published", "value": stats.get("apps", 0), "icon": "📦"},
            {"label": "Developers", "value": stats.get("developers", 0), "icon": "👨‍💻"},
            {"label": "Installations", "value": stats.get("installs", 0), "icon": "📥"},
            {"label": "Countries", "value": stats.get("countries", 0), "icon": "🌍"},
        ],
        "mission": "To democratize app development by providing every developer with the tools, marketplace, and community they need to succeed.",
        "values": [
            {"title": "Developer First", "description": "Everything we build starts with the developer experience.", "icon": "💻"},
            {"title": "Open & Transparent", "description": "Open source at heart, transparent in everything we do.", "icon": "🔓"},
            {"title": "Quality & Security", "description": "Every app is reviewed, tested, and secured.", "icon": "🛡️"},
            {"title": "Community Driven", "description": "Built by the community, for the community.", "icon": "🤝"},
        ],
        "team": team[:12],
        "milestones": milestones[:10],
    }
