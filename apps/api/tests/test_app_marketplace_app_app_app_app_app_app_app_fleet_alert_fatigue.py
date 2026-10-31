from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_alert_fatigue import fleet_alert_fatigue
def test_fatigue():
    r = fleet_alert_fatigue([{"actionable": True}, {"actionable": False}, {"actionable": False}, {"actionable": False}])
    assert r["noise"] == 3
    assert r["noise_pct"] == 75.0
    assert r["fatiguing"]
