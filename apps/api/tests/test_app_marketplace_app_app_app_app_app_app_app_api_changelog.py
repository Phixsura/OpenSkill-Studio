from app.services.app_marketplace_app_app_app_app_app_app_app_api_changelog import generate_api_changelog
def test_changelog():
    r = generate_api_changelog([
        {"endpoint": "/users", "type": "added", "breaking": False},
        {"endpoint": "/orders", "type": "removed", "breaking": True},
    ])
    assert r["breaking"] == 1
    assert r["has_breaking"]
