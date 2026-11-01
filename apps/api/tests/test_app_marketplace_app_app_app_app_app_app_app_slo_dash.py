from app.services.app_marketplace_app_app_app_app_app_app_app_slo_dash import slo_dashboard

def test_dashboard():
    r = slo_dashboard([
        {"name": "availability", "current": 99.99, "target": 99.9},
        {"name": "latency", "current": 99.0, "target": 99.5},
        {"name": "error_rate", "current": 98.0, "target": 99.0},
    ])
    assert r["meeting"] == 1
    assert r["overall_health"] == "red"
