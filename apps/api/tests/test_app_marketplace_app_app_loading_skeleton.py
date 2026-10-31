from app.services.app_marketplace_app_app_loading_skeleton import build_skeleton

def test_card():
    r = build_skeleton(layout="card", count=3)
    assert r["count"] == 3
    assert r["layout"] == "card"
    assert r["animated"]
    assert len(r["items"]) == 3

def test_list():
    r = build_skeleton(layout="list", count=5)
    assert r["count"] == 5
    assert r["items"][0]["rows"][0]["type"] == "avatar"
