from app.services.app_marketplace_app_pagination_helper import paginate_offset, paginate_cursor

def test_offset():
    items = list(range(50))
    r = paginate_offset(items=items, page=2, per_page=10)
    assert r["data"] == list(range(10, 20))
    assert r["meta"]["total_pages"] == 5
    assert r["meta"]["has_next"]
    assert r["meta"]["has_prev"]

def test_offset_last():
    items = list(range(25))
    r = paginate_offset(items=items, page=3, per_page=10)
    assert len(r["data"]) == 5
    assert not r["meta"]["has_next"]

def test_cursor_first():
    items = list(range(50))
    r = paginate_cursor(items=items, cursor=None, limit=10)
    assert len(r["data"]) == 10
    assert r["meta"]["has_more"]
    assert r["meta"]["next_cursor"] is not None

def test_cursor_next():
    items = list(range(50))
    r1 = paginate_cursor(items=items, cursor=None, limit=10)
    r2 = paginate_cursor(items=items, cursor=r1["meta"]["next_cursor"], limit=10)
    assert r2["data"] == list(range(10, 20))

def test_cursor_end():
    items = list(range(5))
    r = paginate_cursor(items=items, cursor=None, limit=10)
    assert not r["meta"]["has_more"]
