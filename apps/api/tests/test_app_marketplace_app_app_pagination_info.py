from app.services.app_marketplace_app_app_pagination_info import build_pagination_info

def test_middle():
    r = build_pagination_info(page=3, per_page=10, total=50)
    assert r["display"] == "21-30 of 50"
    assert r["has_prev"]
    assert r["has_next"]
    assert r["total_pages"] == 5

def test_first():
    r = build_pagination_info(page=1, per_page=20, total=100)
    assert r["display"] == "1-20 of 100"
    assert not r["has_prev"]

def test_empty():
    r = build_pagination_info(page=1, per_page=10, total=0)
    assert r["display"] == "No results"
