from app.services.app_marketplace_app_app_app_marketplace_category_grid import build_category_grid

def test_grid():
    r = build_category_grid()
    assert r["total"] == 12
    assert r["total_apps"] > 1000
    assert r["categories"][0]["id"] == "tools"
