from app.services.app_marketplace_app_app_dropdown_menu import build_dropdown_menu

def test_developer():
    items = [
        {"id": "edit", "label": "Edit", "icon": "✏️"},
        {"id": "delete", "label": "Delete", "icon": "🗑️", "danger": True, "roles": ["admin"]},
        {"id": "share", "label": "Share", "icon": "🔗"},
    ]
    r = build_dropdown_menu(items=items, user_role="developer")
    assert r["total"] == 2  # delete filtered out
    assert not any(i["id"] == "delete" for i in r["items"])

def test_admin():
    items = [
        {"id": "edit", "label": "Edit"},
        {"id": "delete", "label": "Delete", "danger": True, "roles": ["admin"]},
    ]
    r = build_dropdown_menu(items=items, user_role="admin")
    assert r["total"] == 2
    assert r["items"][1]["danger"]
