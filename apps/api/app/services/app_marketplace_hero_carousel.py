"""Marketplace hero carousel — rotate featured apps in hero section."""

import random


def build_hero_carousel(featured_apps: list[dict], *, slots: int = 3) -> list[dict]:
    """Select apps for hero carousel rotation."""
    if len(featured_apps) <= slots:
        return featured_apps
    return random.sample(featured_apps, slots)


def build_hero_slide(app: dict) -> dict:
    return {
        "id": app.get("id"), "name": app.get("name"), "slug": app.get("slug"),
        "tagline": (app.get("description") or "")[:80],
        "category": app.get("category"),
        "icon": app.get("icon_url"),
        "cta_url": f"/marketplace/apps/{app.get('slug', '')}",
    }
