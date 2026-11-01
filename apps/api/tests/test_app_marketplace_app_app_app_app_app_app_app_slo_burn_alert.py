from app.services.app_marketplace_app_app_app_app_app_app_app_slo_burn_alert import calculate_burn_alert, summarize_burn_alerts

def test_page():
    r = calculate_burn_alert(99.9, 50, 3)  # 50% consumed in 3% of window
    assert r["burn_rate"] > 14
    assert r["alert_level"] == "page"
    assert r["critical"]

def test_normal():
    r = calculate_burn_alert(99.9, 50, 50)  # 50% consumed in 50% of window
    assert r["burn_rate"] == 1.0
    assert r["alert_level"] == "none"

def test_summary():
    alerts = [{"alert_level": "page"}, {"alert_level": "ticket"}, {"alert_level": "none"}]
    r = summarize_burn_alerts(alerts)
    assert r["paging"] == 1
    assert r["any_critical"]
