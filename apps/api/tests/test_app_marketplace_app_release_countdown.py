from app.services.app_marketplace_app_release_countdown import create_countdown

def test_future():
    r = create_countdown(app_name="AuthSDK", version="3.0",
        release_date="2099-01-01T00:00:00", features=["Dark mode", "SSO"])
    assert r["days_remaining"] > 0
    assert not r["is_released"]
    assert r["feature_count"] == 2

def test_past():
    r = create_countdown(app_name="App", version="1.0",
        release_date="2020-01-01T00:00:00", features=[])
    assert r["is_released"]
    assert r["days_remaining"] == 0

def test_invalid():
    r = create_countdown(app_name="X", version="1", release_date="not-a-date", features=[])
    assert "error" in r
