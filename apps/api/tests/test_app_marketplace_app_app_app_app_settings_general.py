from app.services.app_marketplace_app_app_app_app_settings_general import build_general_settings, validate_general_settings

def test_build():
    app = {"id": "a1", "name": "SuperApp", "slug": "super-app", "tagline": "Do more",
           "description": "A great app", "icon": "🚀", "category": "tools", "version": "2.0.0"}
    r = build_general_settings(app=app)
    assert len(r["fields"]) == 8
    assert r["current_version"] == "2.0.0"
    name_field = next(f for f in r["fields"] if f["key"] == "name")
    assert name_field["value"] == "SuperApp"

def test_validate_ok():
    r = validate_general_settings(data={"name": "App", "slug": "my-app", "description": "A" * 20})
    assert r["valid"]

def test_validate_fail():
    r = validate_general_settings(data={"name": "", "slug": "BAD!", "description": "short"})
    assert not r["valid"]
    assert len(r["errors"]) >= 3
