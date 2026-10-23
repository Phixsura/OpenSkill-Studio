from app.services.app_marketplace_app_app_cta_button import build_cta

def test_primary():
    r = build_cta(label="Get Started", style="primary", size="lg")
    assert "bg-blue-600" in r["classes"]
    assert "py-3" in r["classes"]
    assert r["label"] == "Get Started"

def test_danger():
    r = build_cta(label="Delete", style="danger", icon="🗑️")
    assert "bg-red-600" in r["classes"]
    assert r["icon"] == "🗑️"

def test_full_width():
    r = build_cta(label="Submit", full_width=True)
    assert "w-full" in r["classes"]
