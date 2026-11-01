from app.services.app_marketplace_app_app_app_app_app_app_app_privacy_display import build_privacy_summary

def test_privacy():
    r = build_privacy_summary({
        "name": "My App", "privacy_url": "https://example.com/privacy",
        "data_collected": ["personal", "usage", "cookies"],
    })
    assert r["data_count"] == 3
    assert r["max_risk"] == "high"
    assert r["has_privacy_policy"]
    assert r["data_collected"][0]["label"] == "Personal Information"

def test_no_policy():
    r = build_privacy_summary({"name": "Test"})
    assert not r["has_privacy_policy"]
    assert r["data_count"] == 0
