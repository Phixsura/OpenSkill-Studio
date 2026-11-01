from app.services.app_marketplace_app_app_app_app_app_app_app_wishlist import Wishlist

def test_wishlist():
    wl = Wishlist()
    wl.add("alice", "app1")
    wl.add("alice", "app2")
    assert wl.count("alice") == 2
    assert wl.is_wishlisted("alice", "app1")
    r = wl.add("alice", "app1")
    assert not r["added"]
    wl.remove("alice", "app1")
    assert not wl.is_wishlisted("alice", "app1")
    assert wl.count("alice") == 1
