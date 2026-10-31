from app.services.app_marketplace_app_app_pagination import offset_paginate, cursor_paginate

def test_offset_first():
    r = offset_paginate(total=50, page=1, page_size=10)
    assert r["total_pages"] == 5
    assert r["offset"] == 0
    assert not r["has_prev"]
    assert r["has_next"]

def test_offset_last():
    r = offset_paginate(total=50, page=5, page_size=10)
    assert r["has_prev"]
    assert not r["has_next"]

def test_cursor():
    items = list(range(25))
    r1 = cursor_paginate(items=items, page_size=10)
    assert len(r1["items"]) == 10
    assert r1["has_more"]
    r2 = cursor_paginate(items=items, page_size=10, cursor=r1["next_cursor"])
    assert r2["items"][0] == 10
    r3 = cursor_paginate(items=items, page_size=10, cursor=r2["next_cursor"])
    assert len(r3["items"]) == 5
    assert not r3["has_more"]
