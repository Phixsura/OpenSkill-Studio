from app.services.app_marketplace_developer_onboarding_checklist import build_onboarding_checklist

def test_partial():
    dev = {"display_name": "Alice", "avatar": "img.png", "email_verified": True,
           "tos_accepted": False, "app_count": 0}
    r = build_onboarding_checklist(developer=dev)
    assert r["completed"] == 2
    assert r["progress_pct"] == 33
    assert not r["onboarding_complete"]

def test_complete():
    dev = {"display_name": "Bob", "avatar": "a.png", "email_verified": True,
           "tos_accepted": True, "app_count": 1, "webhook_count": 1, "has_api_key": True}
    r = build_onboarding_checklist(developer=dev)
    assert r["completed"] == 6
    assert r["onboarding_complete"]
