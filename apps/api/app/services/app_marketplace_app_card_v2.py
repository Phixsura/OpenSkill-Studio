"""App card v2 — rich app card data for marketplace listings."""


def build_app_card_v2(*, app: dict, developer: dict, stats: dict) -> dict:
    rating = stats.get("avg_rating", 0)
    stars = "★" * int(rating) + "☆" * (5 - int(rating))
    badges = []
    if developer.get("verified"):
        badges.append({"type": "verified", "label": "Verified Developer", "icon": "✅"})
    if stats.get("installs", 0) > 1000:
        badges.append({"type": "popular", "label": "Popular", "icon": "🔥"})
    if app.get("is_featured"):
        badges.append({"type": "featured", "label": "Featured", "icon": "⭐"})
    return {
        "id": app["id"], "name": app["name"], "slug": app.get("slug"),
        "description": app.get("short_description", app.get("description", ""))[:120],
        "category": app.get("category"), "icon": app.get("icon"),
        "developer_name": developer.get("display_name"),
        "rating": rating, "stars": stars, "review_count": stats.get("review_count", 0),
        "install_count": stats.get("installs", 0), "badges": badges,
        "price": app.get("price_label", "Free"),
    }


def build_app_card_list(*, apps_data: list[dict]) -> list[dict]:
    return [build_app_card_v2(app=d["app"], developer=d["developer"], stats=d["stats"]) for d in apps_data]
