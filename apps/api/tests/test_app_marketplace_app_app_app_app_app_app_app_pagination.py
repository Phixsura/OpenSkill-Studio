from app.services.app_marketplace_app_app_app_app_app_app_app_pagination import paginate_offset, paginate_cursor

def test_offset():
    r = paginate_offset(total=100, page=3, page_size=10)
    assert r["offset"] == 20
    assert r["total_pages"] == 10
    assert r["has_prev"]
    assert r["has_next"]
    assert r["showing"] == "21-30 of 100"

def test_cursor():
    items = [{"id": f"item-{i}", "name": f"Item {i}"} for i in range(30)]
    r = paginate_cursor(items=items, limit=10)
    assert r["count"] == 10
    assert r["has_more"]
    r2 = paginate_cursor(items=items, cursor=r["next_cursor"], limit=10)
    assert r2["count"] == 10
    r3 = paginate_cursor(items=items, cursor=r2["next_cursor"], limit=10)
    assert r3["count"] == 10
    assert not r3["has_more"]
