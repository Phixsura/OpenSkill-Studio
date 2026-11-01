from app.services.app_marketplace_app_validator import validate_marketplace_ready

def test_ready():
    r = validate_marketplace_ready({"status": "published", "description": "Great app", "visibility": "public", "icon_url": "x", "homepage_url": "y"},
        version={"review_status": "approved"}, developer={"verified": True})
    assert r["ready"] is True
    assert r["errors"] == []

def test_not_published():
    r = validate_marketplace_ready({"status": "draft", "description": "X", "visibility": "public"})
    assert r["ready"] is False

def test_no_description():
    r = validate_marketplace_ready({"status": "published", "visibility": "public"})
    assert r["ready"] is False

def test_unverified_warning():
    r = validate_marketplace_ready({"status": "published", "description": "X", "visibility": "public"},
        developer={"verified": False})
    assert len(r["warnings"]) > 0

def test_no_icon_warning():
    r = validate_marketplace_ready({"status": "published", "description": "X", "visibility": "public"})
    assert any("icon" in w.lower() for w in r["warnings"])
