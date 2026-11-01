from app.services.app_marketplace_app_app_app_create_form import validate_app_creation

def test_valid():
    r = validate_app_creation(name="My Cool App", slug="my-cool-app",
                               description="A really cool app for developers",
                               category="tools")
    assert r["valid"]
    assert r["app"]["slug"] == "my-cool-app"
    assert r["app"]["status"] == "draft"

def test_bad_slug():
    r = validate_app_creation(name="X", slug="BAD SLUG!", description="A" * 20, category="tools")
    assert not r["valid"]

def test_bad_category():
    r = validate_app_creation(name="X", slug="my-app", description="A" * 20, category="nonexistent")
    assert not r["valid"]
