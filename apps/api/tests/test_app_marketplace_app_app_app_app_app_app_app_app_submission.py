from app.services.app_marketplace_app_app_app_app_app_app_app_app_submission import validate_submission, create_submission

def test_valid():
    app = {"name": "My Cool App", "description": "A really cool app for developers to use",
           "category": "tools", "icon_url": "https://example.com/icon.png",
           "developer_name": "Acme Inc"}
    r = validate_submission(app)
    assert r["valid"]

def test_invalid():
    r = validate_submission({"name": "AB"})
    assert not r["valid"]
    assert r["error_count"] >= 4

def test_submission():
    app = {"name": "My Cool App", "description": "A really cool app for developers to use",
           "category": "tools", "icon_url": "https://icon.png", "developer_name": "Acme"}
    r = create_submission(app)
    assert r["status"] == "pending_review"
    assert len(r["review_steps"]) == 4
