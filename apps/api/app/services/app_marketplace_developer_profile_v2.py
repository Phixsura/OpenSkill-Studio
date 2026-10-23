"""Developer profile v2 — complete editable developer profile with validation."""

import re


def validate_profile(*, profile: dict) -> dict:
    errors = []
    name = profile.get("display_name", "")
    if len(name) < 2 or len(name) > 50:
        errors.append("Display name must be 2-50 characters")
    slug = profile.get("slug", "")
    if not re.match(r'^[a-z0-9][a-z0-9-]{1,28}[a-z0-9]$', slug):
        errors.append("Slug must be 3-30 lowercase alphanumeric with hyphens")
    email = profile.get("support_email", "")
    if email and not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        errors.append("Invalid support email")
    bio = profile.get("bio", "")
    if len(bio) > 500:
        errors.append("Bio must be under 500 characters")
    website = profile.get("website", "")
    if website and not website.startswith(("https://", "http://")):
        errors.append("Website must start with https://")
    return {"valid": len(errors) == 0, "errors": errors}


def compute_profile_completeness(*, profile: dict) -> dict:
    fields = {"display_name": 20, "slug": 10, "bio": 15, "support_email": 15,
              "website": 10, "avatar": 15, "social_links": 15}
    completed = 0
    for field, weight in fields.items():
        if profile.get(field):
            completed += weight
    return {"completeness_pct": completed, "complete": completed == 100,
            "missing": [f for f in fields if not profile.get(f)]}


def build_profile_card(*, profile: dict, stats: dict) -> dict:
    return {
        "name": profile.get("display_name"), "slug": profile.get("slug"),
        "bio": profile.get("bio", "")[:120], "avatar": profile.get("avatar"),
        "verified": profile.get("verified", False),
        "stats": {"apps": stats.get("apps", 0), "installs": stats.get("installs", 0),
                   "rating": stats.get("avg_rating", 0)},
        "joined": profile.get("created_at", "")[:10],
    }
