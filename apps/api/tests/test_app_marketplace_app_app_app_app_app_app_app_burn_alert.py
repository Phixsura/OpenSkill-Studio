from app.services.app_marketplace_app_app_app_app_app_app_app_burn_alert import check_burn_alert, should_page

def test_no_alert():
    r = check_burn_alert(0.5, [{"name": "1h", "burn_rate": 0.5, "threshold": 1}])
    assert not r["firing"]

def test_alert():
    r = check_burn_alert(14, [
        {"name": "5m", "burn_rate": 14, "threshold": 1},
        {"name": "1h", "burn_rate": 5, "threshold": 1},
    ])
    assert r["firing"]
    assert r["most_severe"] == "critical"

def test_page():
    alert = {"most_severe": "critical"}
    r = should_page(alert)
    assert r["page"]
    assert r["channel"] == "pagerduty"
