"""App summary builder — compile app summary for developer dashboard list."""

def build_app_summary_list(apps: list[dict]) -> list[dict]:
    return [{
        "id": a.get("id"), "name": a.get("name"), "slug": a.get("slug"),
        "status": a.get("status"), "category": a.get("category"),
        "install_count": a.get("install_count", 0),
        "health_score": a.get("health_score", 100),
        "latest_version": a.get("latest_version"),
        "needs_attention": a.get("status") in ("rejected", "revoked") or a.get("health_score", 100) < 80,
    } for a in apps]
