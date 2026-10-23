from app.services.app_marketplace_wishlist import add_to_wishlist, remove_from_wishlist, check_wishlist_updates, get_wishlist_summary

def test_add():
    r = add_to_wishlist(user_id="u1", app_id="a1", wishlist=[])
    assert r["added"]
    assert r["count"] == 1

def test_add_duplicate():
    r = add_to_wishlist(user_id="u1", app_id="a1", wishlist=["a1"])
    assert not r["added"]

def test_remove():
    r = remove_from_wishlist(app_id="a1", wishlist=["a1", "a2"])
    assert r["removed"]
    assert r["count"] == 1

def test_remove_missing():
    r = remove_from_wishlist(app_id="a3", wishlist=["a1"])
    assert not r["removed"]

def test_updates():
    apps = [{"id": "a1", "name": "App1", "has_new_version": True, "latest_version": "2.0"},
            {"id": "a2", "name": "App2", "price_changed": True, "price_label": "Free"}]
    u = check_wishlist_updates(wishlist_apps=apps)
    assert len(u) == 2

def test_summary():
    apps = [{"id": "a1", "name": "App1", "price_cents": 999}, {"id": "a2", "name": "App2", "price_cents": 0}]
    s = get_wishlist_summary(wishlist=["a1"], apps=apps)
    assert s["count"] == 1
    assert s["total_value"] == 999
