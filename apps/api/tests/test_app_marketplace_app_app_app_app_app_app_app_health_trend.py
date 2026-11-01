from app.services.app_marketplace_app_app_app_app_app_app_app_health_trend import analyze_trend, predict_sla

def test_improving():
    r = analyze_trend([
        {"uptime_pct": 98}, {"uptime_pct": 99}, {"uptime_pct": 99.5},
        {"uptime_pct": 99.9}, {"uptime_pct": 99.99},
    ])
    assert r["trend"] == "improving"
    assert r["worst"] == 98

def test_degrading():
    r = analyze_trend([
        {"uptime_pct": 99.99}, {"uptime_pct": 99.9}, {"uptime_pct": 99.5},
        {"uptime_pct": 99}, {"uptime_pct": 98},
    ])
    assert r["trend"] == "degrading"

def test_predict():
    r = predict_sla({"avg_uptime": 99.95}, sla_target=99.9)
    assert r["on_track"]
    assert r["risk"] == "low"
