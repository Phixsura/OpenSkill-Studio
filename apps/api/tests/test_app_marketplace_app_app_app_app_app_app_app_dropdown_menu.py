from app.services.app_marketplace_app_app_app_app_app_app_app_dropdown_menu import build_menu

def test_menu():
    r = build_menu([
        {"id": "edit", "label": "Edit", "icon": "✏️", "shortcut": "⌘E", "group": "actions"},
        {"id": "duplicate", "label": "Duplicate", "icon": "📋", "group": "actions"},
        {"id": "delete", "label": "Delete", "icon": "🗑️", "group": "danger", "danger": True},
    ])
    assert r["total_items"] == 3
    assert len(r["sections"]) == 2
    assert r["sections"][0]["group"] == "actions"
    assert r["sections"][0]["items"][0]["shortcut"] == "⌘E"
