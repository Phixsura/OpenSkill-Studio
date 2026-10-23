from app.services.app_marketplace_app_app_success_page import build_success_page

def test_installed():
    r = build_success_page(action="installed", resource_name="Auth SDK")
    assert r["icon"] == "🎉"
    assert "Auth SDK" in r["title"]
    assert len(r["next_steps"]) == 2

def test_published():
    r = build_success_page(action="published", resource_name="My App")
    assert r["icon"] == "🚀"
    assert "live" in r["message"]

def test_custom_steps():
    steps = [{"label": "Go Home", "url": "/", "primary": True}]
    r = build_success_page(action="deployed", resource_name="v2", next_steps=steps)
    assert len(r["next_steps"]) == 1
