from app.services.app_marketplace_app_app_app_app_app_app_app_version_sunset import check_sunsets

def test_sunsets():
    r = check_sunsets([
        {"version": "v1", "days_until_sunset": -30},
        {"version": "v2", "days_until_sunset": 60},
        {"version": "v3", "days_until_sunset": 365},
    ])
    assert r["active"] == 1
    assert r["sunsetting"] == 1
    assert r["sunset"] == 1
    assert r["action_needed"]
