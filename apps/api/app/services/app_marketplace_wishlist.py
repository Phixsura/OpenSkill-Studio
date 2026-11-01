"""Wishlist — save apps for later and get notified of updates."""


def add_to_wishlist(*, user_id: str, app_id: str, wishlist: list[str]) -> dict:
    if app_id in wishlist:
        return {"added": False, "reason": "Already in wishlist", "count": len(wishlist)}
    return {"added": True, "wishlist": wishlist + [app_id], "count": len(wishlist) + 1}


def remove_from_wishlist(*, app_id: str, wishlist: list[str]) -> dict:
    if app_id not in wishlist:
        return {"removed": False, "reason": "Not in wishlist", "count": len(wishlist)}
    new_list = [a for a in wishlist if a != app_id]
    return {"removed": True, "wishlist": new_list, "count": len(new_list)}


def check_wishlist_updates(*, wishlist_apps: list[dict]) -> list[dict]:
    updates = []
    for app in wishlist_apps:
        if app.get("has_new_version"):
            updates.append({"app_id": app["id"], "app_name": app["name"],
                             "new_version": app.get("latest_version"), "type": "new_version"})
        if app.get("price_changed"):
            updates.append({"app_id": app["id"], "app_name": app["name"],
                             "type": "price_change", "new_price": app.get("price_label")})
    return updates


def get_wishlist_summary(*, wishlist: list[str], apps: list[dict]) -> dict:
    wishlisted = [a for a in apps if a.get("id") in wishlist]
    return {"count": len(wishlisted), "apps": wishlisted,
            "total_value": sum(a.get("price_cents", 0) for a in wishlisted)}
