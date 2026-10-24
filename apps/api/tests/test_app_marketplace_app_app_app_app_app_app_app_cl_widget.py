from app.services.app_marketplace_app_app_app_app_app_app_app_cl_widget import build_widget, format_type_badge

def test_widget():
    changes = [{"version": "3.5", "title": "SSO", "type": "added", "date": "2026-10-24"}] * 8
    r = build_widget(changes, max_items=5)
    assert r["count"] == 5
    assert r["total"] == 8
    assert r["has_more"]

def test_badge():
    r = format_type_badge("added")
    assert r["emoji"] == "✨"
    assert r["label"] == "New"
