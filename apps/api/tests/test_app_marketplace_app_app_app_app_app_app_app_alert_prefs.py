from app.services.app_marketplace_app_app_app_app_app_app_app_alert_prefs import get_alert_prefs, update_alert, check_alert

def test_prefs():
    prefs = get_alert_prefs()
    assert len(prefs) == 5

def test_update():
    r = update_alert("error_rate", threshold=10.0, channel="slack")
    assert r["threshold"] == 10.0
    assert r["channel"] == "slack"

def test_check():
    # Reset threshold for test
    update_alert("error_rate", threshold=5.0)
    r = check_alert("error_rate", 8.0)
    assert r["triggered"]
    r2 = check_alert("uptime", 99.99)
    assert not r2["triggered"]
    r3 = check_alert("uptime", 99.0)
    assert r3["triggered"]
