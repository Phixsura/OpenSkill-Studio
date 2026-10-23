from app.services.app_marketplace_app_app_loading_skeleton import get_skeleton

def test_app_card():
    r = get_skeleton(template="app_card")
    assert r["template"] == "app_card"
    assert r["row_count"] == 4

def test_multiple():
    r = get_skeleton(template="list_item", count=5)
    assert r["row_count"] == 10
    assert r["count"] == 5

def test_unknown():
    r = get_skeleton(template="magic")
    assert "error" in r
