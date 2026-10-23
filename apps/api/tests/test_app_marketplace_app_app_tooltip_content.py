from app.services.app_marketplace_app_app_tooltip_content import get_tooltip, get_tooltips_by_category

def test_get():
    r = get_tooltip(tooltip_id="api_key")
    assert r["title"] == "API Key"
    assert "authentication" in r["link"]

def test_unknown():
    r = get_tooltip(tooltip_id="magic")
    assert "error" in r

def test_by_category():
    r = get_tooltips_by_category(category="security")
    assert r["count"] >= 1
    assert all(t["category"] == "security" for t in r["tooltips"])
