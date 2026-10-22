"""Marketplace hero builder — build hero section for marketplace home."""

def build_hero(*, total_apps: int, total_developers: int, tagline: str = "Build, publish, and discover apps for OpenSkill") -> dict:
    return {"tagline": tagline, "total_apps": total_apps, "total_developers": total_developers,
            "cta_primary": {"label": "Explore Apps", "url": "/marketplace/apps"},
            "cta_secondary": {"label": "Build an App", "url": "/dashboard/developer"}}
