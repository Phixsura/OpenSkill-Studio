from app.services.app_marketplace_app_app_responsive_grid import build_grid_config

def test_grid():
    r = build_grid_config(items_count=12, min_card_width=280)
    assert r["layouts"]["sm"]["columns"] >= 2
    assert r["layouts"]["lg"]["columns"] >= 3
    assert r["layouts"]["default"]["columns"] == 1
    assert "grid-cols-1" in r["grid_class"]

def test_narrow_cards():
    r = build_grid_config(items_count=20, min_card_width=150)
    assert r["layouts"]["lg"]["columns"] >= 5
