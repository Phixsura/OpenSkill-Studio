from app.services.app_marketplace_app_app_sidebar_layout import build_sidebar_layout

def test_layout():
    sections = [
        {"title": "Main", "items": [
            {"id": "home", "label": "Home", "roles": ["developer", "admin"]},
            {"id": "admin", "label": "Admin", "roles": ["admin"]},
        ]},
    ]
    r = build_sidebar_layout(sections=sections, user_role="developer")
    assert r["total_items"] == 1  # admin filtered out
    assert r["width"] == "w-56"

def test_collapsed():
    r = build_sidebar_layout(sections=[], collapsed=True)
    assert r["width"] == "w-14"
