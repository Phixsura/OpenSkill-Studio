from app.services.app_marketplace_app_marketplace_pagination import paginate, build_page_links

def test_paginate():
    items = list(range(50))
    r = paginate(items=items, page=2, per_page=20)
    assert len(r["data"]) == 20
    assert r["meta"]["total"] == 50
    assert r["meta"]["total_pages"] == 3
    assert r["meta"]["has_prev"]
    assert r["meta"]["has_next"]

def test_first_page():
    r = paginate(items=list(range(10)), page=1, per_page=5)
    assert not r["meta"]["has_prev"]
    assert r["meta"]["has_next"]

def test_links():
    l = build_page_links(base_url="/api/apps", page=2, total_pages=5)
    assert "prev" in l
    assert "next" in l
    assert "page=3" in l["next"]
