from app.services.app_marketplace_app_preview_builder import build_preview

def test_preview():
    p = build_preview({"id": "a1", "name": "App", "slug": "app", "category": "connector", "install_count": 42},
        developer={"display_name": "Dev", "verified": True}, badges=["Popular"])
    assert p["name"] == "App"
    assert p["verified"] is True
    assert len(p["badges"]) == 1

def test_truncate_desc():
    p = build_preview({"description": "x" * 200})
    assert len(p["description"]) <= 120
