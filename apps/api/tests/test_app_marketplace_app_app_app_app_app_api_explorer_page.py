from app.services.app_marketplace_app_app_app_app_app_api_explorer_page import build_api_explorer_page

def test_all():
    r = build_api_explorer_page()
    assert r["total"] == 10
    assert len(r["tags"]) >= 3

def test_filter():
    r = build_api_explorer_page(tag_filter="Webhooks")
    assert r["total"] == 2
    assert all(e["tag"] == "Webhooks" for e in r["endpoints"])
