from app.services.app_marketplace_app_app_app_app_app_app_app_global_nav import build_global_nav, get_section_items

def test_nav():
    r = build_global_nav(active_section="develop")
    assert len(r["sections"]) == 4
    assert r["total_links"] == 17
    dev = next(s for s in r["sections"] if s["id"] == "develop")
    assert dev["active"]

def test_items():
    items = get_section_items("docs")
    assert len(items) == 4
    assert items[0]["label"] == "Getting Started"
