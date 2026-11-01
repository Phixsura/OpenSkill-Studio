from app.services.app_marketplace_app_app_app_app_app_app_app_resp_transform import transform_response, paginate_response

def test_standard():
    r = transform_response({"result": [1, 2, 3]}, "standard")
    assert r["data"] == [1, 2, 3]

def test_envelope():
    r = transform_response({"result": {"id": 1}}, "envelope")
    assert r["success"]
    assert r["error"] is None

def test_paginate():
    items = list(range(50))
    r = paginate_response(items, page=2, per_page=20)
    assert len(r["data"]) == 20
    assert r["data"][0] == 20
    assert r["meta"]["has_next"]
    assert r["meta"]["has_prev"]
    assert r["meta"]["total_pages"] == 3
