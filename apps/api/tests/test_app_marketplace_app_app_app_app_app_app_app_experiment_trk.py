from app.services.app_marketplace_app_app_app_app_app_app_app_experiment_trk import create_experiment, analyze_experiment

def test_create():
    e = create_experiment("new-checkout", "Reduces cart abandonment", "conversion_rate", 3.5, 10)
    assert e["status"] == "running"
    assert e["metric"] == "conversion_rate"

def test_analyze_winner():
    e = create_experiment("test", "h", "metric", 100, 5)
    r = analyze_experiment(e, 112)
    assert r["lift_pct"] == 12.0
    assert r["winner"] == "variant"

def test_inconclusive():
    e = create_experiment("test", "h", "metric", 100, 10)
    r = analyze_experiment(e, 103)
    assert r["winner"] == "inconclusive"
